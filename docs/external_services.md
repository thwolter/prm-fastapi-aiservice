# External Services

This document describes the external services used in the AI Service project.

## OpenMeter

OpenMeter is a service used for metering, entitlements, and payments in the AI Service project.

### OpenMeterClient

The `OpenMeterClient` is an implementation of the `AbstractMeteringClient` interface that interacts with the OpenMeter service for metering-related operations.

#### Initialization

```python
def __init__(self, sync_client: Client, async_client: AsyncClient):
```

- `sync_client`: The synchronous OpenMeter client.
- `async_client`: The asynchronous OpenMeter client.

#### Methods

##### record_usage

```python
def record_usage(self, subject_id: str, usage_event: UsageEvent) -> bool:
```

Records usage for a subject using OpenMeter.

- `subject_id`: The ID of the subject.
- `usage_event`: The usage event data.

##### get_usage

```python
def get_usage(self, subject_id: str) -> TokenQuotaResponse:
```

Gets usage for a subject using OpenMeter.

- `subject_id`: The ID of the subject.


##### list_subjects

```python
def list_subjects(self) -> List[Subject]:
```

Lists all subjects using OpenMeter.

##### ingest_events

```python
def ingest_events(self, events: Dict[str, Any]) -> bool:
```

Ingests events into OpenMeter.

- `events`: The events to ingest.

##### list_entitlements

```python
def list_entitlements(self, subject: Optional[List[str]] = None) -> List[Entitlement]:
```

Lists entitlements using OpenMeter, optionally filtered by subject.

- `subject`: Optional list of subject IDs to filter by.

### OpenMeterEntitlementClient

The `OpenMeterEntitlementClient` is an implementation of the `AbstractEntitlementClient` interface that interacts with the OpenMeter service for entitlement-related operations.

#### Initialization

```python
def __init__(self, sync_client: Client, async_client: AsyncClient):
```

- `sync_client`: The synchronous OpenMeter client.
- `async_client`: The asynchronous OpenMeter client.

#### Methods

##### get_entitlement_value

```python
def get_entitlement_value(self, subject_id: str, feature_key: str) -> Entitlement:
```

Gets the entitlement value for a subject and feature using OpenMeter.

- `subject_id`: The ID of the subject.
- `feature_key`: The feature key to check.

