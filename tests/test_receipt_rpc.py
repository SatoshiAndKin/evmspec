"""The supported decoder must accept the receipt status returned by JSON-RPC."""

import json

import pytest
from msgspec.json import Decoder

from evmspec.data import _decode_hook
from evmspec.structs.receipt import Status, TransactionReceipt


@pytest.mark.parametrize("status,expected", [("0x0", Status.failure), ("0x1", Status.success)])
def test_receipt_status_uses_rpc_hex_values(status: str, expected: Status) -> None:
    payload = {
        "transactionHash": "0x" + "01" * 32,
        "blockNumber": "0x1",
        "transactionIndex": "0x0",
        "contractAddress": None,
        "status": status,
        "gasUsed": "0x5208",
        "cumulativeGasUsed": "0x5208",
        "logs": [],
    }
    receipt = Decoder(type=TransactionReceipt, dec_hook=_decode_hook).decode(json.dumps(payload))
    assert receipt.status is expected
    assert receipt.logs == ()
