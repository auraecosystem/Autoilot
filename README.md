# Autoilot — LMLM Language Foundation

Autoilot is the experimental language and compiler-front-end workspace for LMLM. This foundation defines three distinct source profiles that target one shared intermediate representation (IR) and one policy-governed execution authority.

## Language profiles

| Profile | Extension | Contract |
|---|---|---|
| Native LMLM | `.lmlm` | Independent grammar and language semantics |
| LMLM Python | `.lpy` | Python-compatible source with LMLM decorators and APIs |
| LMLM Hybrid | `.lmx` | Explicit mixed C#-style and Python-style syntax subset |

These are separate frontends, not three runtimes. They must produce equivalent normalized IR for equivalent programs.

## Repository status

This is a **specification and IR-validation foundation**, not yet a complete compiler or execution runtime. The existing `init.cl`, `lmlm.AppleScript`, and unfinished `models.cls` are retained as historical prototypes.

## Layout

- `docs/LANGUAGE_SPEC_v0.1.md` — profile differences, semantics, annotations, diagnostics, and compiler contract.
- `docs/IR_SCHEMA.json` — machine-readable shared IR schema.
- `src/lmlm_ir/validator.py` — dependency-free structural and policy validation.
- `tests/` — IR validation and differential conformance tests.
- `examples/` — equivalent assistant examples in all three profiles.
- `fixtures/differential/` — canonical IR used as the cross-frontend conformance target.

## Validate

Requires Python 3.10+.

```bash
python -m unittest discover -s tests -v
```

## Security boundary

Source annotations express requested configuration; they do not grant permissions. Every frontend must lower to the same IR contract, and the LMLM policy engine must independently authorize every capability before execution. No frontend may execute arbitrary source text or bypass the policy engine.

## Planned implementation stages

1. Lexer/parser and AST for Native LMLM.
2. Python AST frontend and restricted LMLM decorator bridge.
3. Explicit Hybrid grammar and parser with diagnostics for unsupported constructs.
4. Semantic analysis, type checking, and normalized IR lowering.
5. Differential conformance suite across all frontends.
6. Policy engine, model registry, adapters, and runtime integration.

See [the v0.1 language specification](docs/LANGUAGE_SPEC_v0.1.md).
