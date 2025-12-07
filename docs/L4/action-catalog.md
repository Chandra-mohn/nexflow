# L4: Action Catalog

> **Source**: Adapted from rules_engine/ACTIONS_CATALOG.md
> **Status**: Complete Specification

---

## Overview

Actions are the terminal operations of business rules. When a rule matches, it executes one or more actions. This catalog defines 20 credit card domain actions organized by category.

All actions receive the complete `RuleContext` containing all available data.

---

## Action Categories

### Application Processing (6 actions)

#### `rejectApplication`
**Purpose**: Reject a credit card application

**Context Data Needed**:
- `applicant.*` - for logging rejection reasons
- `system.timestamp` - for audit trail

**Usage**:
```
if applicant.creditScore < 500 then rejectApplication
```

---

#### `approveApplication`
**Purpose**: Approve a credit card application with standard terms

**Context Data Needed**:
- `applicant.*` - for account setup
- `card.*` - for credit limit assignment

**Usage**:
```
if applicant.creditScore >= 700 then approveApplication
```

---

#### `instantApproval`
**Purpose**: Immediately approve for high-quality applicants

**Context Data Needed**:
- `applicant.*` - for premium account setup
- `card.*` - for higher credit limits

**Usage**:
```
if applicant.creditScore >= 800 and applicant.annualIncome > 150000 then instantApproval
```

---

#### `conditionalApproval`
**Purpose**: Approve with conditions or restrictions

**Context Data Needed**:
- `applicant.*` - for conditional terms setup
- `card.*` - for restricted credit limits

**Usage**:
```
if applicant.creditScore >= 650 and applicant.creditScore < 700 then conditionalApproval
```

---

#### `manualReview`
**Purpose**: Route application for human review

**Context Data Needed**:
- `applicant.*` - for reviewer context
- `system.*` - for review queue assignment

**Usage**:
```
if applicant.creditScore >= 600 and applicant.bankruptcyHistory = true then manualReview
```

---

#### `requireManualReview`
**Purpose**: Flag application for mandatory manual review (alias)

**Context Data Needed**: Same as `manualReview`

---

### Transaction Authorization (4 actions)

#### `approveTransaction`
**Purpose**: Authorize the transaction to proceed

**Context Data Needed**:
- `transaction.*` - for authorization logging
- `card.*` - for balance updates
- `merchant.*` - for settlement processing

**Usage**:
```
if transaction.amount <= 100 or transaction.merchant.category = "5411" then approveTransaction
```

---

#### `blockTransaction`
**Purpose**: Block/decline the transaction immediately

**Context Data Needed**:
- `transaction.*` - for decline reason logging
- `customer.*` - for notification preferences
- `card.*` - for fraud tracking

**Usage**:
```
if transaction.amount > 10000 and transaction.location != customer.homeLocation then blockTransaction
```

---

#### `decline`
**Purpose**: Decline the transaction (alias for blockTransaction)

**Context Data Needed**: Same as `blockTransaction`

---

#### `temporaryBlock`
**Purpose**: Temporarily block card due to suspicious activity

**Context Data Needed**:
- `card.*` - for block duration and settings
- `customer.*` - for notification and unblock procedures
- `transaction.*` - for block reason documentation

**Usage**:
```
if transaction.velocityCount1h > 10 then temporaryBlock
```

---

### Risk Management (5 actions)

#### `flagForReview`
**Purpose**: Mark transaction for post-processing review

**Context Data Needed**:
- `transaction.*` - for review queue details
- `customer.*` - for risk profile assessment
- `merchant.*` - for merchant risk analysis

**Usage**:
```
if transaction.amount > 5000 and transaction.isOnline = true then flagForReview
```

---

#### `requireVerification`
**Purpose**: Require additional customer verification

**Context Data Needed**:
- `customer.*` - for verification method selection
- `transaction.*` - for verification context
- `merchant.*` - for risk justification

**Usage**:
```
if merchant.riskLevel = "HIGH" then requireVerification
```

---

#### `requirePhoneVerification`
**Purpose**: Require phone-based verification

**Context Data Needed**:
- `customer.*` - for phone number and preferences
- `transaction.*` - for verification details
- `card.*` - for account verification

**Usage**:
```
if transaction.amount > 2000 and transaction.isInternational = true then requirePhoneVerification
```

---

#### `requireStepUpAuth`
**Purpose**: Require enhanced authentication (2FA, biometric)

**Context Data Needed**:
- `customer.*` - for available auth methods
- `transaction.*` - for auth context
- `card.*` - for security settings

**Usage**:
```
if transaction.amount > 5000 then requireStepUpAuth
```

---

#### `requireAdditionalAuth`
**Purpose**: Require additional authentication (generic)

**Context Data Needed**: Same as `requireStepUpAuth`

---

### Communication (3 actions)

#### `sendAlert`
**Purpose**: Send alert notification to customer

**Context Data Needed**:
- `customer.*` - for notification preferences and contact info
- `transaction.*` - for alert content
- `merchant.*` - for transaction context

**Usage**:
```
if transaction.amount > 500 then sendAlert
```

---

#### `sendSMSVerification`
**Purpose**: Send SMS verification code

**Context Data Needed**:
- `customer.*` - for phone number and SMS preferences
- `transaction.*` - for verification context
- `system.*` - for verification code generation

**Usage**:
```
if transaction.isInternational = true then sendSMSVerification
```

---

#### `sendRealTimeAlert`
**Purpose**: Send immediate real-time alert

**Context Data Needed**:
- `customer.*` - for real-time notification channels
- `transaction.*` - for alert urgency and content
- `merchant.*` - for transaction details

**Usage**:
```
if transaction.timeOfDay = "OFF_HOURS" then sendRealTimeAlert
```

---

### Account Management (2 actions)

#### `increaseCreditLimit`
**Purpose**: Increase customer's credit limit

**Context Data Needed**:
- `customer.*` - for new limit calculation
- `card.*` - for current limit and utilization
- `applicant.*` - for income verification

**Usage**:
```
if customer.paymentHistory = "EXCELLENT" and customer.utilizationRate < 0.3 then increaseCreditLimit
```

---

#### `decreaseCreditLimit`
**Purpose**: Decrease customer's credit limit

**Context Data Needed**:
- `customer.*` - for risk assessment
- `card.*` - for current utilization and new limit
- `transaction.*` - for recent activity patterns

**Usage**:
```
if customer.paymentHistory = "POOR" or customer.utilizationRate > 0.9 then decreaseCreditLimit
```

---

## Action Summary Table

| Category | Action | Count |
|----------|--------|-------|
| **Application Processing** | rejectApplication, approveApplication, instantApproval, conditionalApproval, manualReview, requireManualReview | 6 |
| **Transaction Authorization** | approveTransaction, blockTransaction, decline, temporaryBlock | 4 |
| **Risk Management** | flagForReview, requireVerification, requirePhoneVerification, requireStepUpAuth, requireAdditionalAuth | 5 |
| **Communication** | sendAlert, sendSMSVerification, sendRealTimeAlert | 3 |
| **Account Management** | increaseCreditLimit, decreaseCreditLimit | 2 |
| **Total** | | **20** |

---

## Action Implementation Pattern

### Interface Definition

```java
public interface Action {
    void execute(RuleContext context);
}
```

### Example Implementation

```java
public class ApproveTransactionAction implements Action {
    @Override
    public void execute(RuleContext context) {
        // Access any needed data from context
        String transactionId = context.getString("transaction.id");
        BigDecimal amount = context.getMoney("transaction.amount");
        String customerId = context.getString("customer.id");

        // Execute business logic
        transactionService.approve(transactionId, amount, customerId);

        // Log action execution
        auditService.logAction("approveTransaction", context.getData());
    }
}
```

---

## Action Registry

### Registry Pattern

```java
public class ActionRegistry {
    private Map<String, Action> actions = new HashMap<>();

    public void registerAction(String name, Action action) {
        actions.put(name, action);
    }

    public void executeAction(String actionName, RuleContext context) {
        Action action = actions.get(actionName);
        if (action != null) {
            action.execute(context);
        } else {
            throw new ActionNotFoundException("Action not found: " + actionName);
        }
    }
}
```

### Registration

```java
ActionRegistry registry = new ActionRegistry();
registry.registerAction("approveTransaction", new ApproveTransactionAction());
registry.registerAction("blockTransaction", new BlockTransactionAction());
registry.registerAction("flagForReview", new FlagForReviewAction());
// ... register all 20 actions
```

---

## Context Access Patterns

### Full Context Access

Actions receive complete `RuleContext` with full JSON data:

```java
public void execute(RuleContext context) {
    // Access nested attributes
    String status = context.getString("applicant.employment.status");
    int score = context.getInt("applicant.creditScore");
    BigDecimal amount = context.getMoney("transaction.amount");

    // Access arrays
    String country = context.getString("customer.addresses[0].country");

    // Check existence
    if (context.hasValue("customer.vipStatus")) {
        // handle VIP
    }
}
```

### Type-Safe Access

```java
// Primitives
String s = context.getString("path");
int i = context.getInt("path");
double d = context.getDouble("path");
boolean b = context.getBoolean("path");

// Domain types
BigDecimal money = context.getMoney("path");
LocalDate date = context.getDate("path");
Instant timestamp = context.getTimestamp("path");

// With defaults
String status = context.getString("path", "UNKNOWN");
int score = context.getInt("path", 0);
```

---

## Error Handling

### Missing Data

```java
public void execute(RuleContext context) {
    // Required data - fail fast
    String transactionId = context.getRequired("transaction.id");

    // Optional data - use default
    String note = context.getString("transaction.note", "");

    // Conditional processing
    if (context.hasValue("customer.vipStatus")) {
        applyVipProcessing(context);
    }
}
```

### Validation

```java
public void execute(RuleContext context) {
    BigDecimal amount = context.getMoney("transaction.amount");

    if (amount.compareTo(BigDecimal.ZERO) <= 0) {
        throw new InvalidTransactionException("Amount must be positive");
    }

    // proceed with action
}
```

---

## Performance Considerations

1. **Stateless Actions**: Actions should be stateless for thread safety
2. **Cache Context Values**: Cache frequently used values within execution
3. **Minimize External Calls**: Reduce service calls where possible
4. **Async Non-Critical**: Use async for logging, notifications

---

## Related Documents

- [procedural-rules.md](./procedural-rules.md) - Rule syntax
- [decision-tables.md](./decision-tables.md) - Decision table syntax
- [../L4-Business-Rules.md](../L4-Business-Rules.md) - L4 overview
