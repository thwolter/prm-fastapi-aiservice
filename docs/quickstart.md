# Quickstart Guide

This guide will help you get started with the AI Service project, focusing on setting up a subject with entitlement using OpenMeter.

## Prerequisites

Before you begin, make sure you have:

1. Python 3.12 or higher installed
2. Access to the AI Service project repository
3. OpenMeter API credentials (API URL and API key)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd ai-service
```

2. Install dependencies using Poetry:

```bash
poetry install
```

3. Set up environment variables:

```bash
# `OPENMETER_API_KEY` is only needed when using the OpenMeter cloud sandbox.
# It can be omitted when testing against a local instance.
export OPENMETER_API_URL=<your-openmeter-api-url>
export OPENMETER_API_KEY=<your-openmeter-api-key>
```

## Setting Up a Subject with Entitlement

### 1. Create a Subject in OpenMeter

A subject represents a user in the system. You can create a subject directly using the OpenMeter client:

```python
from uuid import uuid4
from src.external.metering.openmeter_client import OpenMeterClient

# Create a metering client
metering_client = OpenMeterClient.from_default_config()

# Create a subject with a new UUID and email
user_id = uuid4()
user_email = "user@example.com"
metering_client.upsert_subject([{
    'key': str(user_id),
    'displayName': user_email
}])

print(f"Created subject with ID: {user_id}")
```

### 2. Verify the Subject in OpenMeter

You can verify that the subject was created correctly by listing all subjects:

```python
# List all subjects
subjects = metering_client.list_subjects()
print(f"Found {len(subjects)} subjects")
for subject in subjects:
    print(f"Subject ID: {subject['key']}, Email: {subject['displayName']}")
```

### 3. Check Entitlement Status

Once a subject has been created and entitlements have been set up in OpenMeter, you can check if the subject has access to a feature using the `EntitlementService`:

```python
from src.domain.services.entitlement_service import EntitlementService
from src.external.entitlements.openmeter_entitlement_client import OpenMeterEntitlementClient

# Create an entitlement client
entitlement_client = OpenMeterEntitlementClient.from_default_config()

# Create an entitlement service for the subject
entitlement_service = EntitlementService(entitlement_client, user_id=user_id)

# Check if the subject has access to the feature
has_access = await entitlement_service.get_token_entitlement_status("api_calls")
print(f"Subject {user_id} has access to api_calls: {has_access}")

# Get the entitlement value
entitlement_value = await entitlement_service.get_entitlement_value("api_calls")
print(f"Entitlement value: {entitlement_value}")
```

## Using the API

The AI Service provides a REST API for managing subjects and checking entitlements. Here are some examples using `curl`:

### Create a Subject

```bash
curl -X POST "http://localhost:8000/api/subjects/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{"id": "00000000-0000-0000-0000-000000000001", "email": "user@example.com"}'
```

### Check Entitlement Status

```bash
curl -X GET "http://localhost:8000/api/entitlements/00000000-0000-0000-0000-000000000001/api_calls" \
  -H "Authorization: Bearer <your-token>"
```

## Next Steps

Now that you have set up a subject with entitlement in OpenMeter, you can:

1. Record usage for the subject
2. Check the subject's usage against their entitlement
3. Explore the API endpoints for more functionality
