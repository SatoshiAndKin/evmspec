# Benchmarks for evmspec

This directory contains native package benchmarks for key hot paths and micro-utilities in `evmspec`:

- `test_address_benchmarks.py`: `Address` constructors, checksum, and decode hooks.
- `test_block_benchmarks.py`: `TinyBlock.transactions` decoding.
- `test_cache_benchmarks.py`: cached call paths.
- `test_decode_hook_benchmarks.py`: global decode hooks and internal helpers.
- `test_decoding_benchmarks.py`: Transaction, receipt, and log decoding.
- `test_enum_benchmarks.py`: canonical RPC string enum conversion and rejection.
- `test_hexbytes_benchmarks.py`: `HexBytes32` construction and helpers.
- `test_numeric_benchmarks.py`: `uint` parsing/formatting, `Wei.scaled`, and timestamps.
- `test_uints_benchmarks.py`: fixed-width uint constructors.

## Running Benchmarks

Install the benchmark dependencies:

```
poetry install --with benchmark
poetry run python -m pip install --no-deps .
```

Run the suite against the installed native package from outside the checkout:

```
PYTHON="$(poetry env info --executable)"
BENCHMARKS="$PWD/benchmarks"
cd /tmp
"$PYTHON" -m pytest "$BENCHMARKS"
```

The benchmark configuration writes `benchmark-results.json` in the current
directory. CI uploads this file as a GitHub artifact. These are local wall-clock
measurements; compare results only under equivalent host and workload conditions.

## Contributing

- Add benchmarks for new public APIs or hot decode paths.
- Keep inputs representative of real RPC payloads.
- Each benchmark should stand alone (no paired reference/optimized variant).
