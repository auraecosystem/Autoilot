# LMLM Language Specification v0.1

**Status:** Draft / implementation baseline  
**Project:** Autoilot  
**Scope:** Three source profiles, shared semantics, common IR, and differential conformance.

## 1. Design

LMLM supports three independent source frontends:

- **Native** (`.lmlm`): LMLM-owned syntax and semantics.
- **Python-compatible** (`.lpy`): Python syntax plus a constrained LMLM API/decorator layer.
- **Hybrid** (`.lmx`): a separately parsed, explicitly bounded mixture of C#-style declarations and Python-style directives.

All frontends lower to the same normalized IR. The IR is the only input accepted by the future execution planner. A frontend is never an execution authority.

## 2. Differential characteristics

| Dimension | Native | Python-compatible | Hybrid |
|---|---|---|---|
| Grammar owner | LMLM | Python grammar plus LMLM API | LMLM hybrid grammar |
| Source compatibility | LMLM language | Selected Python versions/features | Explicit supported subset |
| Type model | LMLM types | Python annotations, validated at boundary | C#-style static declarations plus LMLM types |
| Imports | LMLM modules | Python imports through allowlisted resolver | `using` and `from ... import` forms |
| Annotations | `@name(...)` | Python decorators/type hints | Shared annotation syntax |
| Async | Native async semantics | Python `async/await` | C#-style `async/await` subset |
| Main advantage | Language sovereignty | Ecosystem and developer velocity | Interoperability and migration |
| Main cost | New compiler/tooling | Python compatibility and isolation | Highest parser and semantic complexity |

Hybrid does not promise that arbitrary C# and Python programs can be mixed. Unsupported syntax must produce a source-located diagnostic; it must not be guessed or silently translated.

## 3. Shared annotations

The following annotation names have shared meanings across profiles:

- `@runtime(target="local")`: requested execution target.
- `@model(provider="builtin", name="default")`: model selection request.
- `@security(policy="restricted")`: requested policy profile.
- `@capability(["inference"])`: declared capability requirements.
- `@timeout(seconds=60)`: requested execution deadline.
- `@verify(mode="required")`: output verification requirement.

Annotations are declarative metadata. They do not grant permissions. The policy engine makes the final authorization decision.

## 4. Import and initialization semantics

The initial prototype contains these forms:

```text
using System;
from __future__ import annotations;
using __local__ import models;
using __ini__;
using in-builtModel;
```

The v0.1 interpretation is:

- `System`, `System.Linq`, and `System.Data.Objects` are Hybrid namespace examples, not proof that the .NET framework is embedded.
- `from __future__ import annotations` is Python-only and is accepted in the Python profile; Hybrid may accept it only in its Python-directive region.
- `using __local__ import models` requests the LMLM local-model registry.
- `using __ini__` requests the LMLM initialization module.
- `using in-builtModel` is legacy spelling for the built-in model registry. New code should use `LMLM.Models.Builtin`.
- Imports are resolved by a frontend-specific allowlist. They cannot load arbitrary modules or assemblies.

Initialization is an explicit lifecycle operation. Importing a module must not implicitly start model inference, access remote services, or execute arbitrary code.

## 5. Native profile (.lmlm)

Illustrative source:

```lmlm
module LMLM.Assistant;

import LMLM.Models.Builtin;
import LMLM.Runtime;

@runtime(target: "local")
@model(provider: "builtin", name: "default")
@security(policy: "restricted")
@capability(["inference"])
@verify(mode: "required")

model Assistant {
    initialize() {
        model.load("default");
    }

    execute(input: Text) -> Response {
        return model.generate(input);
    }
}
```

Native owns its lexical rules, parser, type checker, module resolution, and diagnostics. The grammar and standard library are versioned independently from Python and .NET.

## 6. Python-compatible profile (.lpy)

Illustrative source:

```python
from __future__ import annotations

from lmlm import runtime
from lmlm.models import builtin

@runtime(target="local")
@builtin.model("default")
class Assistant:
    async def execute(self, prompt: str) -> str:
        model = await builtin.load()
        return await model.generate(prompt)
```

The Python frontend parses Python source into a Python AST, validates imports and supported syntax, resolves LMLM decorators, then lowers the validated program to common IR. It must not use `eval`, unrestricted `exec`, or import arbitrary modules as a substitute for compilation.

Python type hints are checked at the LMLM boundary; they are not treated as runtime security controls.

## 7. Hybrid profile (.lmx)

Illustrative source:

```lmx
using System;
using System.Linq;
using LMLM.Models.Local;

from __future__ import annotations;

using __ini__;

@runtime(target="local")
@model(provider="local", name="default")
@security(policy="restricted")

class Assistant {
    public async Task<string> Execute(string prompt) {
        var model = await models.load("default");
        return await model.generate(prompt);
    }
}
```

Hybrid uses a dedicated grammar with explicit regions:
1. C#-style namespace/import and class/member declarations.
2. Python-style future directives where permitted.
3. LMLM annotations and model/runtime APIs.

The parser must reject ambiguous mixed constructs. C# namespaces do not imply the availability of the full .NET Base Class Library. Each supported namespace and API requires an explicit adapter or compiler implementation.

## 8. Shared intermediate representation

The first supported operation is `model.generate`. Its normalized IR has this shape:

```json
{
  "operation": "model.generate",
  "provider": "local",
  "model": "default",
  "input": {
    "type": "text",
    "source": "user_input"
  },
  "permissions": ["inference"],
  "verification": {
    "required": true
  }
}
```

IR fields are validated against `IR_SCHEMA.json`. Unknown fields and unsupported operations fail closed. The IR describes a request; it does not itself authorize execution.

## 9. Compiler frontend contract

Each frontend must expose equivalent stages:

1. Parse source into a frontend-specific AST.
2. Resolve imports against an allowlist.
3. Validate syntax, types, annotations, and supported APIs.
4. Produce normalized IR.
5. Submit IR to the shared policy engine.
6. Execute only an authorized plan through LMLM Core.
7. Return structured results and auditable diagnostics.

Recommended conceptual interface:

```text
Frontend.parse(source) -> AST | Diagnostics
Frontend.analyze(AST) -> TypedProgram | Diagnostics
Frontend.lower(TypedProgram) -> IR | Diagnostics
IRValidator.validate(IR) -> ValidationResult
PolicyEngine.authorize(IR, principal) -> Decision
Runtime.execute(AuthorizedPlan) -> ExecutionResult
```

## 10. Diagnostics

Diagnostics should include a stable code, message, source profile, source span when available, and remediation hint. Minimum categories:

- `E_IMPORT_NOT_ALLOWED`
- `E_SYNTAX_UNSUPPORTED`
- `E_ANNOTATION_INVALID`
- `E_TYPE_MISMATCH`
- `E_IR_INVALID`
- `E_CAPABILITY_DENIED`
- `E_MODEL_NOT_FOUND`

## 11. Differential conformance

Equivalent programs across Native, Python, and Hybrid must produce the same normalized IR for the same task. Tests compare normalized IR, validation decisions, capability requirements, and error categories. Formatting and source spans may differ; execution authority and requested semantics may not.

A frontend that emits broader permissions, a different provider, or a different model for an equivalent fixture fails conformance.

## 12. Explicit non-goals for v0.1

- Full C# or Python language compatibility.
- Arbitrary native library or assembly loading.
- Arbitrary source-code execution.
- A production model-serving implementation.
- Remote execution without an explicit policy-governed adapter.
- Treating annotations as authorization.

These are deliberate boundaries, not implied capabilities.
