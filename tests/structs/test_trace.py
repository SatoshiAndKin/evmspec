import json

import pytest
from faster_hexbytes import HexBytes  # type: ignore [import-not-found]
from msgspec import Raw, ValidationError
from msgspec.json import decode, encode

from evmspec.data import _decode_hook
from evmspec.structs.trace import FilterTrace

from evmspec.data import Address, BlockHash, BlockNumber, TransactionHash, Wei, uint

pytest.importorskip("dictstruct")

from evmspec.structs.trace import call, create, reward, suicide

ADDRESS = "0x" + "11" * 20
ADDRESS_2 = "0x" + "22" * 20
TX_HASH = "0x" + "33" * 32
BLOCK_HASH = "0x" + "44" * 32


def _raw(value) -> Raw:
    return Raw(json.dumps(value).encode())


def _base_trace_kwargs() -> dict[str, object]:
    return {
        "blockNumber": BlockNumber(1),
        "blockHash": BlockHash(BLOCK_HASH),
        "transactionHash": TransactionHash(TX_HASH),
        "transactionPosition": 0,
        "traceAddress": [uint(0)],
        "subtraces": uint(0),
    }


def test_call_trace_action_decode() -> None:
    action = {
        "from": ADDRESS,
        "value": "0x1",
        "gas": "0x5208",
        "callType": "call",
        "to": ADDRESS_2,
        "input": "0x",
    }
    trace = call.Trace(_action=_raw(action), result=None, **_base_trace_kwargs())
    decoded = trace.action
    assert decoded.callType is call.Type.call
    assert decoded.sender == Address(ADDRESS)
    assert trace.block == BlockNumber(1)


def test_create_trace_action_decode() -> None:
    action = {
        "from": ADDRESS,
        "value": "0x0",
        "gas": "0x5208",
        "init": "0x6000",
        "creationMethod": "create",
    }
    result = create.Result(
        gasUsed=Wei(21_000),
        address=Address(ADDRESS),
        code=HexBytes("0x6000"),
    )
    trace = create.Trace(_action=_raw(action), result=result, **_base_trace_kwargs())
    decoded = trace.action
    assert decoded.init == HexBytes("0x6000")


def test_create_trace_action_validation_error_logs(caplog) -> None:
    trace = create.Trace(_action=_raw({}), result=None, **_base_trace_kwargs())
    with pytest.raises(ValidationError):
        _ = trace.action
    assert "error decoding" in caplog.text


@pytest.mark.parametrize("reward_type", ["block", "uncle"])
def test_reward_trace_action_decode(reward_type) -> None:
    payload = {
        "type": "reward",
        "action": {"author": ADDRESS_2, "value": "0x1", "rewardType": reward_type},
        "blockNumber": 1,
        "blockHash": BLOCK_HASH,
        "traceAddress": [],
        "subtraces": 0,
        "result": None,
    }
    trace = decode(json.dumps(payload).encode(), type=FilterTrace, dec_hook=_decode_hook)
    assert type(trace) is reward.Trace
    assert trace.action.rewardType is reward.Type(reward_type)
    assert trace.action.rewardType.value == reward_type
    assert trace.action.author == Address(ADDRESS_2)
    assert trace.action.value == Wei(1)
    assert trace.action is trace.action
    assert trace.block == BlockNumber(1)
    assert trace.result is None
    assert not hasattr(trace, "transactionHash")
    assert not hasattr(trace, "transactionPosition")
    assert decode(encode(trace._action)) == payload["action"]


def test_mainnet_block_one_reward() -> None:
    # Captured from Reth trace_block("0x1") on Ethereum mainnet.
    payload = {
        "action": {
            "author": "0x05a56e2d52c817161883f50c441c3228cfe54d9f",
            "rewardType": "block",
            "value": "0x4563918244f40000",
        },
        "blockHash": "0x88e96d4537bea4d9c05d12549907b32561d3bf31f45aae734cdc119f13406cb6",
        "blockNumber": 1,
        "result": None,
        "subtraces": 0,
        "traceAddress": [],
        "type": "reward",
    }
    trace = decode(json.dumps(payload).encode(), type=FilterTrace, dec_hook=_decode_hook)
    assert trace.action.author == Address(payload["action"]["author"])
    assert trace.action.value == Wei(5 * 10**18)
    assert trace.action.rewardType is reward.Type.block
    assert trace.action is trace.action
    assert decode(encode(trace._action)) == payload["action"]


@pytest.mark.parametrize("call_type", ["call", "delegatecall", "staticcall"])
def test_call_type_rpc_roundtrip(call_type) -> None:
    action = {
        "from": ADDRESS,
        "value": "0x1",
        "gas": "0x5208",
        "callType": call_type,
        "to": ADDRESS_2,
        "input": "0x1234",
    }
    trace = call.Trace(_action=_raw(action), result=None, **_base_trace_kwargs())
    assert trace.action.callType is call.Type(call_type)
    assert trace.action.callType.value == call_type
    assert trace.action.input == HexBytes("0x1234")
    assert trace.action.gas == Wei(21000)
    assert trace.action.value == Wei(1)
    assert trace.action is trace.action
    assert decode(encode(trace, enc_hook=str))["action"] == action
    assert decode(encode(trace.action, enc_hook=str))["callType"] == call_type


@pytest.mark.parametrize("enum_cls", [call.Type, reward.Type])
@pytest.mark.parametrize("invalid", [0, 1, 2, "0", "invalid", "CALL", None])
def test_trace_enum_rejects_non_rpc_values(enum_cls, invalid) -> None:
    with pytest.raises(ValueError):
        enum_cls(invalid)


@pytest.mark.parametrize("invalid", [0, 1, "invalid", None])
@pytest.mark.parametrize("kind", ["call", "reward"])
def test_invalid_action_type_is_rejected(kind, invalid) -> None:
    if kind == "call":
        action = {
            "from": ADDRESS,
            "value": "0x0",
            "gas": "0x0",
            "to": ADDRESS_2,
            "input": "0x",
            "callType": invalid,
        }
        trace = call.Trace(_action=_raw(action), result=None, **_base_trace_kwargs())
    else:
        action = {"author": ADDRESS, "value": "0x0", "rewardType": invalid}
        trace = reward.Trace(
            _action=_raw(action),
            result=None,
            blockNumber=BlockNumber(1),
            blockHash=BlockHash(BLOCK_HASH),
            traceAddress=[],
            subtraces=uint(0),
        )
    with pytest.raises(ValidationError):
        _ = trace.action


@pytest.mark.parametrize("trace_type", ["call", "create", "suicide"])
@pytest.mark.parametrize("missing", ["transactionHash", "transactionPosition"])
def test_transaction_trace_requires_metadata(trace_type, missing) -> None:
    action = {"from": ADDRESS, "value": "0x0", "gas": "0x5208"}
    payload = {
        "blockNumber": 1,
        "blockHash": BLOCK_HASH,
        "transactionHash": TX_HASH,
        "transactionPosition": 0,
        "traceAddress": [],
        "subtraces": 0,
        "type": trace_type,
        "action": action,
        "result": None,
    }
    if trace_type == "create":
        payload["result"] = {"gasUsed": "0x5208", "address": ADDRESS, "code": "0x00"}
    del payload[missing]
    with pytest.raises(ValidationError, match=missing):
        decode(encode(payload), type=FilterTrace, dec_hook=_decode_hook)


def test_suicide_trace() -> None:
    action = suicide.Action(sender=Address(ADDRESS), value=Wei(1), gas=Wei(21_000))
    trace = suicide.Trace(action=action, result=None, **_base_trace_kwargs())
    assert trace.type == "suicide"
    assert trace.action.sender == Address(ADDRESS)


def test_reward_trace_without_result() -> None:
    payload = {
        "type": "reward",
        "action": {"author": ADDRESS, "value": "0x0", "rewardType": "block"},
        "blockNumber": 1,
        "blockHash": BLOCK_HASH,
        "traceAddress": [],
        "subtraces": 0,
    }
    trace = decode(encode(payload), type=FilterTrace, dec_hook=_decode_hook)
    assert trace.action.rewardType is reward.Type.block
    assert decode(encode(trace._action)) == payload["action"]
