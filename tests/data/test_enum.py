import pytest
from msgspec.json import decode, encode

from evmspec.structs.trace import call, reward


@pytest.mark.parametrize("enum_cls", [call.Type, reward.Type])
def test_trace_enum_wire_values(enum_cls) -> None:
    for member in enum_cls:
        assert member.value == member.name
        assert enum_cls(member.value) is member
        assert enum_cls(member) is member
        assert decode(encode(member)) == member.name
