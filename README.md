# securiCAD Model SDK

A Python SDK for managing models for [foreseeti's securiCAD](https://foreseeti.com/securicad/) products.

## Installation

Install `securicad-model` with pip:

```shell
pip install securicad-model
```

## Overview

This package contains a class `Model` which can be used to read and write models in JSON and sCAD formats.

### Loading language from a `.mar` file

Models with a loaded `.mar` file (created by [malc](https://github.com/mal-lang/malc)) will not permit changes that would make the model invalid. Lower bound multiplicity and attacker errors are still permitted and should be checked manually. The example below uses [vehicleLang](https://github.com/mal-lang/vehicleLang).

```python
from securicad.langspec import Lang
from securicad.model import Model, json_serializer

# Create model with a loaded language.
vehicle_lang = Lang("org.mal-lang.vehiclelang-1.0.0.mar")
model = Model(lang=vehicle_lang)

# Create ECU, Firmware, and Attacker objects.
ecu = model.create_object("ECU")
firmware = model.create_object("Firmware")
attacker = model.create_attacker()

# Connect ECU and Firmware. Allow the attacker to upload malicious firmware.
ecu.field("firmware").connect(firmware.field("hardware"))
attacker.connect(ecu.attack_step("maliciousFirmwareUpload"))

# Assert that there are no multiplicity or attacker errors.
assert len(model.multiplicity_errors) == 0
assert len(model.attacker_errors) == 0
# This can also be done using the `.validate()` method.
assert len(model.validate()) == 0

# Print the model.
print(json_serializer.serialize_model(model))
```

### Specifying language ID and version

Strict validation using `.mar` files is not required, instead language ID and version may be specified. This will allow invalid models to be read and written, something that may be useful when updating models across language versions. The example below uses a fictional vehicleLang version `4.6.8`.
```python
from securicad.model import Model

# Create model with a language ID and version.
model = Model(lang_id="org.mal-lang.vehiclelang", lang_version="4.6.8")

# Construct model...
```

### Working with `.sCAD`

`.sCAD` files can be read and written directly by the SDK, with or without language validation.
```python
from securicad.langspec import Lang
from securicad.model import scad_serializer

# Load truck.sCAD model with validation.
vehicle_lang = Lang("org.mal-lang.vehiclelang-1.0.0.mar")
model = scad_serializer.deserialize_model("truck.sCAD", lang=vehicle_lang)

# Save the model as an sCAD.
scad_serializer.serialize_model(model, "saved.sCAD")
```
```python
from securicad.model import scad_serializer

# Load truck.sCAD model without validation.
model = scad_serializer.deserialize_model("truck.sCAD", lang_id="org.mal-lang.vehiclelang", lang_version="4.6.8")
```
## Examples

```python
# Create a model with a single attacker connected to a PC. Assert that the model is valid and print it.
from securicad.model import Model, json_serializer

model = Model(lang_id="my.custom.lang", lang_version="1.0.0")
machine = model.create_object("Machine", "PC")
attacker = model.create_attacker()
machine.attack_step("compromise").meta["consequence"] = 5
attacker.connect(machine.attack_step("compromise"))

# Assert that there are no mulitplicity or attacker errors.
assert len(model.validate()) == 0

print(json_serializer.serialize_model(model))
```
```python
# Model a connection between a phone and its server. Compromising the phone takes some additional time.
from securicad.model import Model, json_serializer
from securicad.langspec import TtcDistribution, TtcFunction

model = Model(lang_id="my.custom.lang", lang_version="1.0.0")
server = model.create_object("Server", "Mainframe")
client = model.create_object("Client", "iPhone")
server.field("phones").connect(client.field("server"))
client.attack_step("access").ttc = TtcFunction(TtcDistribution.EXPONENTIAL, [0.5]) + 2
attacker = model.create_attacker()
attacker.connect(client.attack_step("access"))

# Assert that there are no mulitplicity or attacker errors.
assert len(model.validate()) == 0

print(json_serializer.serialize_model(model))
```


## License

Copyright © 2020-2022 [Foreseeti AB](https://foreseeti.com)

Licensed under the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0)
