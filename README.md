## evmspec

A collection of [msgspec.Struct](https://jcristharif.com/msgspec/structs.html) definitions for use with the Ethereum Virtual Machine

[Why msgspec?](https://jcristharif.com/msgspec/why.html)

Inspired by [snek3](http://github.com/banteg/snek3), I took the structs and extended them with some extra functionality. 

#### Trace wire values

Call and reward enum values match JSON-RPC strings: `call`, `delegatecall`,
`staticcall`, `block`, and `uncle`. Member names stay the same; `.value` now
returns the string. Numeric values are rejected.

Reward actions contain `author`, `value`, and `rewardType`. Reward traces carry
block metadata without transaction metadata, and preserve an optional null
`result`. Call, create, and suicide traces require transaction hash and position.

#### Type checking
- Run `poetry run mypy` (uses the `pyproject.toml` configuration).

#### Deprecation roadmap
- Planned v1 naming/deprecation finalization is tracked in [#264](https://github.com/BobTheBuidler/evmspec/issues/264).
- Minor releases keep backward-compatible block struct behavior while we converge on the final v1 public contract.

#### Modules:
- [block](https://bobthebuidler.github.io/evmspec/source/evmspec.html#module-evmspec.structs.block)
- [log](https://bobthebuidler.github.io/evmspec/source/evmspec.html#module-evmspec.log)
- [receipt](https://bobthebuidler.github.io/evmspec/source/evmspec.html#module-evmspec.receipt)
- [trace](https://bobthebuidler.github.io/evmspec/source/evmspec.structs.trace.html)
- [transaction](https://bobthebuidler.github.io/evmspec/source/evmspec.html#module-evmspec.transaction)
- and more
  

### Decoder compatibility

This fork requires `msgspec==0.19.0`, the version used by the tested pricing stack.
Newer decoders bypass the receipt status metaclass and reject valid RPC hex statuses
such as `"0x1"`. The dependency pin preserves the existing `Status.success` and
`Status.failure` members and their integer values. Receipt regressions exercise
actual JSON-RPC hex statuses, independently of trace enum string tests.
