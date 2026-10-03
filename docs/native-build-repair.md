# Reproducible native build dependencies

Retain the optional transaction `blockTimestamp` schema repair from
`f0df0d9d8e4e7a7000580054ce2c0b6b6193a14c` and replace the unavailable
`cchecksum==0.3.9` build dependency with the immutable owned-buffer repair
`fff7e1fe87f4679ec96de1cebb1cdd8f5e94be44`. Use the native compiler fork at
`18a37e099bba69872e38adaee3319c125c97048e`, including its bytes ownership repair.
Two obsolete typing suppressions are removed; decoding behavior is unchanged.

A clean isolated macOS ARM64 Python 3.12 wheel build succeeds. Tests installed
that wheel outside the source tree with the safe checksum revision under
`PYTHONMALLOC=debug` and `PYTHONFAULTHANDLER=1`. Import inspection confirms
`evmspec._new` resolves to the new `cpython-312-darwin.so` extension.

The complete suite returns 365 passes and two failures in trace action enum
inputs. The unchanged compiled original revision returns exactly the same 365
passes and two failures; those existing enum failures are independent of this
build dependency repair. Transaction timestamp, modern block, data and schema
regressions pass. Generated C artifacts are excluded from this authored change.
The Poetry lock describes unchanged runtime/development dependencies; isolated
build requirements remain immutable in `pyproject.toml`.
