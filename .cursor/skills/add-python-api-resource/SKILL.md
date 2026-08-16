---
name: add-python-api-resource
description: Add a merchant API resource to the MainMoney Python SDK from OpenAPI
---

# Add a Python API resource

1. Read the pinned contract `contrib/contract/openapi/merchants.openapi.yaml`
   (and `contrib/contract/resources.md`). Cross-check live
   `/api/v1/schema/merchants/` if the pin may be behind. Do not invent endpoints.
2. Add a typed method on the client with pytest coverage.
3. Update README with the installer-facing call only.
