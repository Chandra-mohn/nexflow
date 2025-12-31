#### Nexflow DSL Toolchain
#### Author: Chandra Mohn

# Excel Schema Importer Specification

Import enterprise data models from Excel workbooks into Nexflow Schema DSL.

**Status**: Design Complete
**Priority**: High
**Last Updated**: 2025-12-31

---

## Overview

Enterprise data models often exist in Excel workbooks with thousands of attributes across multiple service domains. This tool imports those definitions into Nexflow `.schema` files, preserving:

- Hierarchical entity relationships (unlimited depth)
- Cross-domain references (Shortcut Entities)
- Business qualifiers (BOM, BQ, CR)
- Persistence patterns (Master, Event, Ledger)
- PII/PCI compliance markers
- Enum definitions scoped to entity/attribute

---

## Excel Workbook Structure

### Sheets (per Service Domain workbook)

| Sheet | Purpose | Required |
|-------|---------|----------|
| BusinessArea | Ignore | No |
| BusinessDomain | Ignore | No |
| ServiceDomain | Domain metadata | Yes |
| Entities | Schema/type definitions | Yes |
| Attributes | Field definitions | Yes |
| Relationships | Parent-child composition | Yes |
| Enumerations | Enum values | Yes |
| ServiceOperations | API contracts (future) | No |

---

## Column Specifications

### ServiceDomain Sheet

| Column | Description |
|--------|-------------|
| Name | Attribute name (look for "Service Domain Name") |
| Value | The service domain name value |

**Usage**: Extract domain name where `Name = "Service Domain Name"`.

---

### Entities Sheet

| Column | Mapping | Notes |
|--------|---------|-------|
| EntityName | `@entity` annotation | Original business name |
| EntityCode | Internal reference | Used for relationships |
| ObjectType | Entity classification | `Entity` or `Shortcut Entity` |
| CollectionName | Schema name + `@collection` | Java Record name, DB collection |
| Pattern | `@pattern` annotation | `Master`, `Event`, `Ledger`, or blank |
| Stereotype | Type modifier | `Array`, `Enum`, or blank |
| EntityQualifier | `@qualifier` annotation | `BOM`, `BQ`, `CR`, or blank |
| BIMEntityName | `@managed` flag | Present = this domain owns CRUD |
| Comment | `@description` annotation | Entity documentation |
| CreationDate | Ignored | Metadata |
| ModificationDate | Ignored | Metadata |
| Creator | Ignored | Metadata |
| Modifier | Ignored | Metadata |
| XPosition | Ignored | Diagram layout |
| YPosition | Ignored | Diagram layout |

**ObjectType Values**:
- `Entity`: Normal entity defined in this domain
- `Shortcut Entity`: Reference to entity in another domain (`@external`)

**Pattern Values**:
- `Master`: Reference/lookup data (slow-changing)
- `Event`: Immutable event records (append-only)
- `Ledger`: Auditable transaction records
- Blank: No specific pattern

**EntityQualifier Values**:
- `BOM`: Business Object Model - core business entities
- `BQ`: Business Qualifier - reference/lookup data
- `CR`: Control Record - operational/processing metadata
- Blank: Unclassified

---

### Attributes Sheet

| Column | Mapping | Notes |
|--------|---------|-------|
| EntityName | Parent entity | Links to Entities sheet |
| EntityCode | Parent entity code | Alternative link |
| Name | Field name (camelCase) | Converted to Java standard |
| Code | Internal reference | Used for relationships |
| Datatype | Field type | See type mapping |
| Length | `@length` or `@precision` | For strings/decimals |
| MandatoryFlag | `required` keyword | Y/N |
| PrimaryIdentifierFlag | `@primary` annotation | Y/N |
| ForeignIdentifierFlag | `@foreign` annotation | Y/N |
| ForeignIdentifierParentEntityName | Reference target | Foreign key target |
| ForeignIdentifierParentEntityCode | Reference target code | Alternative link |
| JSONName | `@json` annotation | Serialization name |
| PIIPCIIndicator | `@pii` or `@pci` | Compliance markers |
| Stereotype | Type modifier | `Enum` links to Enumerations |
| IdentifierType | Identifier classification | Primary/Foreign/Natural |
| Domain | Logical domain | Business categorization |
| Comment | `@description` | Field documentation |
| PrimaryCopybookFieldName | Legacy reference | COBOL integration |
| ObjectType | Ignored | |
| CreationDate | Ignored | Metadata |
| ModificationDate | Ignored | Metadata |
| Creator | Ignored | Metadata |
| Modifier | Ignored | Metadata |

**Datatype Mapping**:

| Excel Datatype | Nexflow Type |
|----------------|--------------|
| String, VARCHAR, CHAR | `string` |
| Integer, INT, NUMBER (no decimal) | `int` |
| Long, BIGINT | `long` |
| Decimal, FLOAT, NUMBER (with decimal) | `decimal` |
| Boolean, BOOL | `boolean` |
| Date | `date` |
| DateTime, Timestamp, TIMESTAMP | `timestamp` |
| BLOB, Binary, BYTES | `bytes` |

---

### Relationships Sheet

| Column | Mapping | Notes |
|--------|---------|-------|
| RelationshipName | Relationship identifier | Documentation |
| RelationshipCode | Internal reference | |
| ParentEntity | Parent schema | Contains the child |
| ChildEntity | Child schema | Nested in parent |
| RelationshipType | Cardinality | `1:1` or `1:n` |
| JoinAttributes | `@join` annotation | Join key fields |
| Stereotype | Composition type | `composition` = inline |
| Comment | Documentation | |
| ObjectType | Ignored | |
| CreationDate | Ignored | Metadata |
| ModificationDate | Ignored | Metadata |
| Creator | Ignored | Metadata |
| Modifier | Ignored | Metadata |

**RelationshipType Mapping**:
- `1:1`: Single nested object field
- `1:n`: `array of ChildEntity` field

**Stereotype**:
- `composition`: Child is embedded in parent (not a reference)

---

### Enumerations Sheet

| Column | Mapping | Notes |
|--------|---------|-------|
| EntityName | Parent entity | Scope of enum |
| AttributeName | Parent attribute | Scope of enum |
| Value | Enum constant | UPPER_SNAKE_CASE |
| Label | Display label | Human-readable |

**Enum Naming**: `{EntityName}{AttributeName}` in PascalCase
- Example: Entity=Order, Attribute=status → `OrderStatus`

---

### ServiceOperations Sheet (Future)

| Column | Description |
|--------|-------------|
| ServiceOperationName | Operation identifier |
| ActionTerm | Business action (Exchange, Execute, Initiate, Request, Retrieve, Update) |
| ServiceGroupType | Operation type (Instanciation, Invocation, Report) |
| EndpointUrl | API endpoint |
| ActionVerb | HTTP verb (Get, Put, Post) |
| ServiceOperationRequest | Request schema reference |
| ServiceOperationResponse | Response schema reference |

**Status**: Hold - existing Java code generator handles this.

---

## Naming Conventions

All names follow Java standards:

| Element | Convention | Example |
|---------|------------|---------|
| Schema name | PascalCase | `Order`, `OrderLineItem` |
| Enum name | PascalCase | `OrderStatus` |
| Field name | camelCase | `orderId`, `lineItems` |
| Constant | UPPER_SNAKE | `PENDING`, `CONFIRMED` |

**CollectionName Handling**:
- If present: Use as schema name (convert to PascalCase)
- If blank: Convert EntityName to PascalCase

**Conversion Examples**:
```
orders           → Order
order_line_items → OrderLineItem
Order            → Order (no change)
order line item  → OrderLineItem
```

---

## Entity Classification Logic

```
IF BIMEntityName is present:
    → @managed (this domain owns CRUD operations)

ELSE IF ObjectType = "Shortcut Entity":
    → @external (reference to another domain)

ELSE:
    → Child/supporting entity (no special marker)
```

**Multiple BIM Entities**: A service domain can have multiple managed aggregates (e.g., Orders domain manages both Order and Return aggregates).

---

## Generated Schema Format

### Full Entity Example

**Input**:
```
Entities:
  EntityName: Order
  CollectionName: orders
  Pattern: Event
  EntityQualifier: BOM
  BIMEntityName: Order

Attributes:
  EntityName: Order | Name: orderId | Datatype: String | PrimaryIdentifierFlag: Y | MandatoryFlag: Y | JSONName: order_id
  EntityName: Order | Name: customerId | Datatype: String | ForeignIdentifierFlag: Y | ForeignIdentifierParentEntityName: Customer | MandatoryFlag: Y
  EntityName: Order | Name: totalAmount | Datatype: Decimal | Length: 18,2 | MandatoryFlag: Y
  EntityName: Order | Name: status | Datatype: String | Stereotype: Enum | MandatoryFlag: Y
  EntityName: Order | Name: piiData | Datatype: String | PIIPCIIndicator: PII

Relationships:
  ParentEntity: Order | ChildEntity: OrderLineItem | RelationshipType: 1:n | Stereotype: composition

Enumerations:
  EntityName: Order | AttributeName: status | Value: PENDING | Label: Pending
  EntityName: Order | AttributeName: status | Value: CONFIRMED | Label: Confirmed
  EntityName: Order | AttributeName: status | Value: SHIPPED | Label: Shipped
```

**Output `Order.schema`**:
```
schema Order
    @version "1.0.0"
    @entity "Order"
    @collection "orders"
    @pattern Event
    @qualifier BOM
    @managed

    orderId: string required
        @primary
        @json "order_id"

    customerId: string required
        @foreign Customer

    totalAmount: decimal required
        @precision 18,2

    status: OrderStatus required

    piiData: string
        @pii

    lineItems: array of OrderLineItem
        @composition
end

enum OrderStatus
    @version "1.0.0"
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    SHIPPED = "Shipped"
end
```

### Shortcut Entity Example

**Without `--resolve-shortcuts`**:
```
schema Address
    @version "1.0.0"
    @entity "Address"
    @external
    # WARNING: Shortcut entity - source domain unknown
    # Run with --resolve-shortcuts to validate
end
```

**With `--resolve-shortcuts`**:
```
schema Address
    @version "1.0.0"
    @entity "Address"
    @external "customers/Address"
end
```

---

## CLI Interface

### Basic Usage

```bash
# Import single workbook
nexflow schema import Orders.xlsx --output ./schemas/orders/

# Import with explicit domain name
nexflow schema import Orders.xlsx --domain orders --output ./schemas/

# Preview without writing files
nexflow schema import Orders.xlsx --dry-run

# Verbose output with mapping details
nexflow schema import Orders.xlsx --verbose
```

### Multi-Domain Import

```bash
# Import all domain workbooks with cross-reference validation
nexflow schema import ./data-models/*.xlsx --resolve-shortcuts --output ./schemas/

# Import specific domains
nexflow schema import Orders.xlsx Customers.xlsx Products.xlsx --resolve-shortcuts --output ./schemas/
```

### Filtering Options

```bash
# Import only managed entities (with BIMEntityName)
nexflow schema import Orders.xlsx --managed-only --output ./schemas/

# Exclude control records
nexflow schema import Orders.xlsx --exclude-qualifiers CR --output ./schemas/

# Include only specific patterns
nexflow schema import Orders.xlsx --patterns Event,Ledger --output ./schemas/
```

### Output Options

```bash
# Generate dependency manifest
nexflow schema import Orders.xlsx --output ./schemas/ --manifest

# Generate domain summary report
nexflow schema import Orders.xlsx --output ./schemas/ --report
```

---

## Output Structure

```
schemas/
├── orders/                          # Service Domain
│   ├── _domain.yaml                 # Domain metadata
│   ├── Order.schema                 # Managed aggregate
│   ├── OrderLineItem.schema         # Child entity
│   ├── Return.schema                # Another managed aggregate
│   ├── ReturnLineItem.schema        # Child entity
│   ├── Customer.schema              # @external shortcut
│   ├── Address.schema               # @external shortcut
│   └── enums/
│       ├── OrderStatus.schema       # Order.status enum
│       └── ReturnReason.schema      # Return.reason enum
├── customers/                       # Another domain
│   ├── _domain.yaml
│   ├── Customer.schema              # Managed here
│   └── Address.schema               # Managed here
└── _dependencies.yaml               # Cross-domain manifest
```

### _domain.yaml

```yaml
name: Orders
description: Order management service domain
managed_entities:
  - Order
  - Return
external_references:
  - entity: Customer
    source: unknown  # or "customers" with --resolve-shortcuts
  - entity: Address
    source: unknown
generated_at: 2025-12-31T10:00:00Z
source_file: Orders.xlsx
```

### _dependencies.yaml

```yaml
orders:
  depends_on:
    customers:
      - Customer
      - Address

customers:
  depends_on: []

products:
  depends_on:
    customers:
      - Supplier
```

---

## Validation and Errors

### Errors (Abort Import)

| Error | Description |
|-------|-------------|
| `MISSING_SHEET` | Required sheet not found |
| `MISSING_COLUMN` | Required column not found |
| `INVALID_DATATYPE` | Unknown datatype in Attributes |
| `ORPHAN_ATTRIBUTE` | Attribute references non-existent entity |
| `ORPHAN_RELATIONSHIP` | Relationship references non-existent entity |
| `DUPLICATE_ENTITY` | Same CollectionName appears twice |
| `CIRCULAR_COMPOSITION` | Composition cycle detected |

### Warnings (Continue with Warning)

| Warning | Description |
|---------|-------------|
| `SHORTCUT_UNRESOLVED` | Shortcut entity source domain unknown |
| `MISSING_COLLECTION_NAME` | CollectionName blank, using EntityName |
| `ENUM_NO_VALUES` | Attribute has Stereotype=Enum but no enum values |
| `EMPTY_RELATIONSHIP` | Relationship with no child records |
| `PII_NO_HANDLER` | PII field without protection strategy |

---

## Implementation Components

### Module Structure

```
backend/
├── importers/
│   ├── __init__.py
│   ├── excel/
│   │   ├── __init__.py
│   │   ├── parser.py           # Excel reading (openpyxl)
│   │   ├── models.py           # Internal data models
│   │   ├── graph.py            # Relationship graph builder
│   │   ├── validator.py        # Validation rules
│   │   └── generator.py        # Schema DSL generator
│   └── schema_importer.py      # Main orchestrator
├── cli/
│   └── commands/
│       └── schema_import.py    # CLI command
```

### Dependencies

```
openpyxl>=3.1.0  # Excel file reading
```

---

## Future Enhancements

1. **Service Operations**: Generate API contract schemas from ServiceOperations sheet
2. **Schema Diff**: Compare imported schemas with existing schemas
3. **Incremental Import**: Update only changed entities
4. **Reverse Export**: Generate Excel from existing schemas
5. **Validation Rules**: Import business validation rules from additional sheets

---

## References

- [Schema DSL Reference](../L2-SchemaDSL-Reference.md)
- [Developer Guide](../DeveloperGuide.md)
