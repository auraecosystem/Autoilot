module LMLM.Assistant;

import System;
import LMLM.Models;
import LMLM.Runtime;

@runtime(target: "local")
@model(provider: "builtin")
@security(policy: "restricted")

model Assistant {
    initialize() {
        load builtin.model("default");
    }

    execute(input: Text) -> Response {
        return infer(input);
    }
}



