import json
from pathlib import Path

import pytest
from msgspec import UNSET, ValidationError
from msgspec.json import Decoder, encode

from evmspec.data import UnixTimestamp, _decode_hook
from evmspec.structs.transaction import (
    Transaction,
    Transaction1559,
    Transaction2930,
    Transaction7702,
)

PAYLOADS = json.loads(
    (
        Path(__file__).parents[1] / "fixtures/mainnet-transactions-with-block-timestamp.json"
    ).read_text()
)
TYPES = {"0x1": Transaction2930, "0x2": Transaction1559, "0x4": Transaction7702}
DECODE = Decoder(type=Transaction, dec_hook=_decode_hook).decode


@pytest.mark.parametrize("payload", PAYLOADS, ids=lambda value: value["type"])
@pytest.mark.parametrize("timestamp", [UNSET, None, "0x0", "0x649af747"])
def test_transaction_block_timestamp(payload, timestamp):
    wire = dict(payload)
    if timestamp is UNSET:
        del wire["blockTimestamp"]
    else:
        wire["blockTimestamp"] = timestamp

    transaction = DECODE(encode(wire))

    assert type(transaction) is TYPES[payload["type"]]
    assert transaction.hash.hex() == payload["hash"]
    assert transaction.blockNumber == int(payload["blockNumber"], 16)
    assert transaction.blockHash.hex() == payload["blockHash"]
    if timestamp is UNSET:
        assert not hasattr(transaction, "blockTimestamp")
    elif timestamp is None:
        assert transaction.blockTimestamp is timestamp
    else:
        assert type(transaction.blockTimestamp) is UnixTimestamp
        assert transaction.blockTimestamp == int(timestamp, 16)


@pytest.mark.parametrize("payload", PAYLOADS, ids=lambda value: value["type"])
def test_transaction_block_timestamp_keeps_unknown_field_validation(payload):
    with pytest.raises(ValidationError, match="unexpectedField"):
        DECODE(encode({**payload, "unexpectedField": True}))
