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

This class needs to be created with either [securicad-enterprise-sdk](https://github.com/foreseeti/securicad-enterprise-sdk) or [securicad-vanguard-sdk](https://github.com/foreseeti/securicad-vanguard-sdk).

### securiCAD Vanguard SDK

```python
import securicad.vanguard

client = securicad.vanguard.client("username", "password")
model = client.get_model(data=aws_data)
```

### securiCAD Enterprise SDK

```python
import securicad.enterprise

client = securicad.enterprise.client(
    base_url="enterprise_url",
    username="username",
    password="password",
    org="organization",
)

project = client.projects.get_project_by_name("My Project")
model_info = client.models.get_model_by_name(project, "My Model")
model = model_info.get_model()
```

## Configure model

Once you have created an instance of the `Model` class, you can configure the attack steps of the model either by disabling them, or by assigning a consequence to them, marking their asset as a high value asset.

### Disable attack steps

Attack steps can be disabled with the method `disable_attacksteps`.

The following snippet disables the attack step `ReadObject` on all `S3Bucket` objects:

```python
model.disable_attackstep("S3Bucket", "ReadObject")
```

The following snippet disables the attack step `ReadObject` on `S3Bucket` objects with the name `my-bucket`:

```python
model.disable_attackstep("S3Bucket", "ReadObject", name="my-bucket")
```

### High value assets

You can set high value assets with the method `set_high_value_assets`.
It takes one parameter, `high_value_assets`, that must be a list of high value asset specifications, e.g.

```python
model.set_high_value_assets(
    high_value_assets=[
        {
            "metaconcept": "EC2Instance",
            "attackstep": "HighPrivilegeAccess",
            "consequence": 7,
        },
        {
            "metaconcept": "DynamoDBTable",
            "attackstep": "AuthenticatedRead",
            "id": {
                "type": "name",
                "value": "VanguardTable",
            },
        },
        {
            "metaconcept": "S3Bucket",
            "attackstep": "AuthenticatedWrite",
            "id": {
                "type": "tag",
                "key": "arn",
                "value": "arn:aws:s3:::my_corporate_bucket/",
            },
        },
    ]
)
```

A high value asset specification is a dictionary that must contain the keys `metaconcept` and `attackstep`.
If the key `consequence` is present, its value must be an integer greater than or equal to 0 and less than or equal to 10.
The default consequence 10 is used if the key `consequence` is omitted.
Any asset in the model that has an attack step with a consequence greater than 0 is considered a high value asset.

The first high value asset specification above sets the consequence to 7 on the attack step `HighPrivilegeAccess` on all `EC2Instance` objects.

The second high value asset specification above sets the consequence to 10 on the attack step `AuthenticatedRead` on `DynamoDBTable` objects with the name `VanguardTable`.

The third high value asset specification above sets the consequence to 10 on the attack step `AuthenticatedWrite` on `S3Bucket` objects with the tag `"arn": "arn:aws:s3:::my_corporate_bucket/"`.

## License

Copyright © 2020-2021 [Foreseeti AB](https://foreseeti.com)

Licensed under the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0)
