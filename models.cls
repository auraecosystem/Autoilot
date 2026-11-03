using System;
using System.Linq;
using System.Data.Objects;

from __future__ import annotations;

using __local__ import models;
using __ini__;

using in-builtModel;

@runtime(target="local")
@model(provider="builtin")

class Assistant {
    public async Task<string> Execute(string prompt) {
        var model = await models.load("default");
        return a
