# Domain Models

This document describes the domain models available in the AI Service project.

## Subject

The `Subject` model represents a subject (user) in the system.

### Fields

- `id`: UUID - The unique identifier for the subject.
- `email`: Optional[str] - The email address of the subject.
- `display_name`: Optional[str] - The display name of the subject.

### Methods

#### to_dict

```python
def to_dict(self):
```

Converts the subject to a dictionary format suitable for external APIs.


## Entitlement

The `Entitlement` model represents an entitlement in the system.

### Fields

- `feature_key`: str - The key of the feature the entitlement is for.
- `has_access`: bool - Whether the subject has access to the feature.
- `balance`: Optional[int] - The remaining balance of the entitlement.
- `limit`: Optional[int] - The limit of the entitlement.
- `usage`: Optional[int] - The usage of the entitlement.
- `period`: Optional[str] - The period of the entitlement.

### Methods

#### from_dict

```python
@classmethod
def from_dict(cls, data: dict) -> 'Entitlement':
```

Creates an Entitlement instance from a dictionary.

#### to_dict

```python
def to_dict(self) -> dict:
```

Converts the entitlement to a dictionary format suitable for external APIs.

## EntitlementCreate

The `EntitlementCreate` model is used for creating a new entitlement.

### Fields

- `feature`: str - The key of the feature the entitlement is for.
- `max_limit`: int - The maximum limit of the entitlement.
- `period`: Literal['DAY', 'WEEK', 'MONTH', 'YEAR'] - The period of the entitlement.

