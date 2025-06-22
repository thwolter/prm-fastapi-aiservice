# Subscription and Payment

> **Note:** The functionality described in this document is not yet implemented, but is planned for future development.

This document describes the process of creating a subscription and arranging payment in the AI Service project.

## Creating a Subscription

A subscription associates a subject (user) with a plan for a specific period. You can create a subscription using the `SubscriptionService`.

### Using the SubscriptionService

```python
from uuid import UUID
from datetime import datetime, timedelta
from src.domain.services.subscription_service import SubscriptionService
from src.domain.services.payment_service import PaymentService
from src.external.payment.openmeter_payment_client import OpenMeterPaymentClient

# Create a payment client
payment_client = OpenMeterPaymentClient.from_default_config()

# Create a payment service
payment_service = PaymentService(payment_client)

# Create a subscription service
subscription_service = SubscriptionService(payment_service)

# Create a subscription
subject_id = UUID("00000000-0000-0000-0000-000000000001")  # Replace with your subject ID
plan_id = "premium_plan"
start_date = datetime.now()
end_date = start_date + timedelta(days=30)  # 30-day subscription
auto_renew = True
metadata = {"source": "api", "promotion_code": "WELCOME10"}
amount = 29.99
currency = "USD"
payment_method = "credit_card"

subscription = await subscription_service.create_subscription(
    subject_id=subject_id,
    plan_id=plan_id,
    start_date=start_date,
    end_date=end_date,
    auto_renew=auto_renew,
    metadata=metadata,
    amount=amount,
    currency=currency,
    payment_method=payment_method
)

print(f"Created subscription with ID: {subscription.id}")
```

### Using the API

You can also create a subscription using the REST API:

```bash
curl -X POST "http://localhost:8000/api/subscriptions/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{
    "subject_id": "00000000-0000-0000-0000-000000000001",
    "plan_id": "premium_plan",
    "start_date": "2023-01-01T00:00:00Z",
    "end_date": "2023-01-31T00:00:00Z",
    "auto_renew": true,
    "metadata": {"source": "api", "promotion_code": "WELCOME10"},
    "amount": 29.99,
    "currency": "USD",
    "payment_method": "credit_card"
  }'
```

## Arranging Payment

When you create a subscription with an amount, the payment is automatically processed. However, you can also process payments separately using the `PaymentService`.

### Using the PaymentService

```python
from uuid import UUID
from src.domain.services.payment_service import PaymentService
from src.external.payment.openmeter_payment_client import OpenMeterPaymentClient

# Create a payment client
payment_client = OpenMeterPaymentClient.from_default_config()

# Create a payment service
payment_service = PaymentService(payment_client)

# Process a payment
subscription_id = UUID("00000000-0000-0000-0000-000000000002")  # Replace with your subscription ID
amount = 29.99
currency = "USD"
payment_method = "credit_card"
metadata = {"type": "subscription_renewal"}

payment = await payment_service.process_payment(
    subscription_id=subscription_id,
    amount=amount,
    currency=currency,
    payment_method=payment_method,
    metadata=metadata
)

print(f"Processed payment with ID: {payment.id}")
```

### Using the API

You can also process a payment using the REST API:

```bash
curl -X POST "http://localhost:8000/api/payments/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{
    "subscription_id": "00000000-0000-0000-0000-000000000002",
    "amount": 29.99,
    "currency": "USD",
    "payment_method": "credit_card",
    "metadata": {"type": "subscription_renewal"}
  }'
```

## Managing Subscriptions

### Getting a Subscription

You can get a subscription by ID:

```python
subscription_id = UUID("00000000-0000-0000-0000-000000000002")  # Replace with your subscription ID
subscription = await subscription_service.get_subscription(subscription_id)
print(f"Subscription: {subscription}")
```

### Getting Subscriptions for a Subject

You can get all subscriptions for a subject:

```python
subject_id = UUID("00000000-0000-0000-0000-000000000001")  # Replace with your subject ID
subscriptions = await subscription_service.get_subscriptions_for_subject(subject_id)
print(f"Found {len(subscriptions)} subscriptions for subject {subject_id}")
```

### Updating a Subscription

You can update a subscription:

```python
subscription_id = UUID("00000000-0000-0000-0000-000000000002")  # Replace with your subscription ID
updated_subscription = await subscription_service.update_subscription(
    subscription_id=subscription_id,
    status="active",
    end_date=datetime.now() + timedelta(days=60),  # Extend to 60 days
    auto_renew=True,
    metadata={"extended": True}
)
print(f"Updated subscription: {updated_subscription}")
```

### Cancelling a Subscription

You can cancel a subscription:

```python
subscription_id = UUID("00000000-0000-0000-0000-000000000002")  # Replace with your subscription ID
cancelled_subscription = await subscription_service.cancel_subscription(
    subscription_id=subscription_id,
    refund=True  # Issue a refund
)
print(f"Cancelled subscription: {cancelled_subscription}")
```

## Managing Payments

### Getting a Payment

You can get a payment by ID:

```python
payment_id = UUID("00000000-0000-0000-0000-000000000003")  # Replace with your payment ID
payment = await payment_service.get_payment(payment_id)
print(f"Payment: {payment}")
```

### Getting Payments for a Subscription

You can get all payments for a subscription:

```python
subscription_id = UUID("00000000-0000-0000-0000-000000000002")  # Replace with your subscription ID
payments = await payment_service.get_payments_for_subscription(subscription_id)
print(f"Found {len(payments)} payments for subscription {subscription_id}")
```

### Refunding a Payment

You can refund a payment:

```python
payment_id = UUID("00000000-0000-0000-0000-000000000003")  # Replace with your payment ID
refunded_payment = await payment_service.refund_payment(
    payment_id=payment_id,
    amount=10.00  # Partial refund of $10.00
)
print(f"Refunded payment: {refunded_payment}")
```

### Updating Payment Status

You can update the status of a payment:

```python
payment_id = UUID("00000000-0000-0000-0000-000000000003")  # Replace with your payment ID
updated_payment = await payment_service.update_payment_status(
    payment_id=payment_id,
    status="failed"
)
print(f"Updated payment status: {updated_payment}")
```
