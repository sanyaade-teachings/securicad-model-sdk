# securiCAD Model SDK

A Python SDK for managing models for [foreseeti's securiCAD](https://foreseeti.com/securicad/) products

## Installation

Install `securicad-model` with pip:

```shell
pip install securicad-model
```

## Overview

This package contains a class `Model`. It can be imported with:

```python
from securicad.model import Model
```

When working with models, you can also load a language as a `.mar` file (created by [malc](https://github.com/mal-lang/malc)). Working on a model with a language loaded will not permit changes that would make the model invalid. Models also have a list of attacker and multiplicity errors that need to be checked manually.

A deserialized model with a loaded language may be in an invalid state. After deserializing a model, you must call `model.validate()` which returns a list of errors. Usage examples can be found in `tests/model/`.

## Examples
```python
# Create a model with a single attacker connected to a PC. Assert that the model is valid and print it.
from securicad.model import Model

model = Model()
machine = model.create_object("Machine", "PC")
attacker = model.create_attacker()
machine.attack_step("compromise").meta["consequence"] = 5
attacker.connect(machine.attack_step("compromise"))

assert not model.multiplicity_errors
assert not model.attacker_errors

print(model.to_dict())
```
```python
# Model a connection between a phone and its server. Compromising the phone takes some additional time.
from securicad.model import Model
from securicad.langspec import TtcDistribution, TtcFunction

model = Model()
server = model.create_object("Server", "Mainframe")
client = model.create_object("Client", "iPhone")
model.create_association(server, "phones", client, "server")
client.attack_step("access").ttc = TtcFunction(TtcDistribution.EXPONENTIAL, [0.5]) + 2
attacker = model.create_attacker()
attacker.connect(client.attack_step("access"))

assert not model.multiplicity_errors
assert not model.attacker_errors

print(model.to_dict())
```


## License

Copyright © 2020-2021 [Foreseeti AB](https://foreseeti.com)

Licensed under the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0)
