from collections.abc import Callable
from enum import Enum
from functools import cached_property
from typing import ClassVar, Final, Literal, final

from dictstruct import LazyDictStruct
from msgspec import UNSET, Raw, field
from msgspec.json import Decoder

from evmspec.data import Address, Wei, _decode_hook
from evmspec.structs.trace._base import _BlockTraceBase


@final
class Type(Enum):
    """Represents the types of rewards in Ethereum: block or uncle.

    This enum is used to specify the type of reward in Ethereum traces.

    Attributes:
        block (str): Represents a block reward.
        uncle (str): Represents an uncle reward.

    Example:
        >>> reward_type = Type.block
        >>> print(reward_type)
        Type.block
    """

    block = "block"
    uncle = "uncle"


@final
class Action(  # type: ignore [misc]
    LazyDictStruct,
    frozen=True,
    kw_only=True,
    forbid_unknown_fields=True,
    omit_defaults=True,
    repr_omit_defaults=True,
):
    """Action type for rewards.

    Rewards contain the author, value, and reward type. They do not have
    a transaction sender or gas allocation.

    Attributes:
        author (Address): The author of this reward.
        rewardType (Type): The type of the reward.

    Example:
        >>> action = Action(author=Address("0x123"), rewardType=Type.block)
        >>> print(action.author)
        0x123
    """

    value: Wei
    """The reward amount in Wei."""

    author: Address
    """The author of this reward."""

    rewardType: Type
    """The type of the reward."""


@final
class Trace(  # type: ignore [misc]
    _BlockTraceBase,
    tag="reward",
    frozen=True,
    kw_only=True,
    forbid_unknown_fields=True,
    omit_defaults=True,
    repr_omit_defaults=True,
):
    """Represents the trace for a reward in Ethereum.

    This class extends :class:`_BlockTraceBase` and is specifically tagged
    as a "reward" trace. It includes raw data for the reward action that
    requires decoding.

    Attributes:
        type (ClassVar[Literal["reward"]]): A class variable indicating the trace type.
        _action (Raw): Raw data of the reward action, requires decoding to be useful.

    Example:
        >>> trace = Trace(blockNumber=123, blockHash=BlockHash("0xabc"), traceAddress=[], subtraces=0, _action=Raw(b'...'))
        >>> decoded_action = trace.action
        >>> print(decoded_action.rewardType)
        Type.block

    See Also:
        - :class:`Action`: The decoded action object.
        - :class:`_BlockTraceBase`: The base class for trace representations.
    """

    type: ClassVar[Literal["reward"]] = "reward"
    """A class-level constant identifying the trace type as a reward trace.

    This attribute is used to distinguish this trace from other types of traces
    within the Ethereum Virtual Machine (EVM).

    Examples:
        >>> Trace.type
        'reward'
    """

    _action: Raw = field(name="action")
    """Raw data of the reward action, requires decoding to be useful."""

    result: None = UNSET  # type: ignore [assignment]
    """An optional null result, preserved when supplied by the node."""

    @cached_property
    def action(self) -> Action:
        """Decodes the raw reward action into an :class:`Action` object, using parity style.

        This method uses the :func:`msgspec.json.decode` function with a
        decoding hook to convert the raw action data into a structured
        :class:`Action` object.

        Returns:
            The decoded action.

        Example:
            >>> trace = Trace(blockNumber=123, blockHash=BlockHash("0xabc"), traceAddress=[], subtraces=0, _action=Raw(b'...'))
            >>> action = trace.action
            >>> print(action.author)
            0x123
        """
        return _decode_action(self._action)


_decode_action: Final[Callable[[Raw], Action]] = Decoder(type=Action, dec_hook=_decode_hook).decode
