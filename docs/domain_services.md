# Domain Services

This document describes the domain services available in the AI Service project.

<!-- The SubjectService section has been removed as part of the removal of SubjectService. -->


## EntitlementService

The `EntitlementService` is responsible for managing entitlements in the system.

### Initialization

```python
def __init__(
    self,
    entitlement_client: AbstractEntitlementClient,
    request: Optional[Request] = None,
    user_id: Optional[UUID] = None,
):
```

- `entitlement_client`: The entitlement client used to interact with the entitlement service.
- `request`: Optional FastAPI request object.
- `user_id`: Optional UUID of the user. If not provided and request is available, it will be extracted from request.state.

### Methods


#### get_token_entitlement_status

```python
async def get_token_entitlement_status(self, feature_key: str) -> bool:
```

Checks if a user has access to a feature.

- `feature_key`: The feature key to check.

#### has_access

```python
async def has_access(self, feature_key: str) -> bool:
```

Alias for `get_token_entitlement_status` for backward compatibility.

- `feature_key`: The feature key to check.

#### get_entitlement_value

```python
async def get_entitlement_value(self, feature_key: str) -> Entitlement:
```

Gets the entitlement value for a user.

- `feature_key`: The feature key to check.
