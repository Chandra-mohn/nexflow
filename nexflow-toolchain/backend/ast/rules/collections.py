# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Rules AST Collection Expression Types

Collection expression types for the Rules DSL.
RFC: Collection Operations Instead of Loops in L4
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Union, TYPE_CHECKING

from .common import SourceLocation, FieldPath
from .enums import ComparisonOp, LogicalOp

if TYPE_CHECKING:
    from .expressions import ValueExpr


class CollectionFunctionType(Enum):
    """Types of collection functions."""
    # Predicate functions - return boolean
    ANY = "any"
    ALL = "all"
    NONE = "none"

    # Aggregate functions - return single value
    SUM = "sum"
    COUNT = "count"
    AVG = "avg"
    MAX = "max"
    MIN = "min"

    # Transform functions - return collection or element
    FILTER = "filter"
    FIND = "find"
    DISTINCT = "distinct"


@dataclass
class CollectionPredicateComparison:
    """Simple comparison predicate: field op value."""
    field: FieldPath
    operator: ComparisonOp
    value: 'ValueExpr'
    location: Optional[SourceLocation] = None


@dataclass
class CollectionPredicateIn:
    """Set membership predicate: field in (values) or field not in (values)."""
    field: FieldPath
    values: List['ValueExpr']
    negated: bool = False
    location: Optional[SourceLocation] = None


@dataclass
class CollectionPredicateNull:
    """Null check predicate: field is null or field is not null."""
    field: FieldPath
    is_not_null: bool = False
    location: Optional[SourceLocation] = None


@dataclass
class CollectionPredicateNot:
    """Negated predicate: not predicate."""
    predicate: 'CollectionPredicateAtom'
    location: Optional[SourceLocation] = None


CollectionPredicateAtom = Union[
    CollectionPredicateComparison,
    CollectionPredicateIn,
    CollectionPredicateNull,
    CollectionPredicateNot,
    'CollectionPredicateCompound'
]


@dataclass
class CollectionPredicateCompound:
    """Compound predicate with AND/OR."""
    predicates: List[CollectionPredicateAtom]
    operators: List[LogicalOp] = field(default_factory=list)  # AND/OR between predicates
    location: Optional[SourceLocation] = None


@dataclass
class LambdaPredicate:
    """Lambda expression predicate: x -> expression."""
    parameter: str
    body: 'ValueExpr'
    location: Optional[SourceLocation] = None


@dataclass
class MultiParamLambdaPredicate:
    """Multi-parameter lambda: (x, y) -> expression."""
    parameters: List[str]
    body: 'ValueExpr'
    location: Optional[SourceLocation] = None


CollectionPredicate = Union[
    CollectionPredicateAtom,
    CollectionPredicateCompound,
    LambdaPredicate,
    MultiParamLambdaPredicate
]


@dataclass
class CollectionExpr:
    """
    Collection expression for functional operations on collections.

    Examples:
    - any(transactions, amount > 1000)
    - all(items, status = "active")
    - sum(orders, total)
    - count(items)
    - filter(transactions, type in ("A", "B"))
    - find(items, id = search_id)

    RFC: Collection Operations Instead of Loops in L4
    """
    function_type: CollectionFunctionType
    collection: 'ValueExpr'
    predicate: Optional[CollectionPredicate] = None  # For any/all/none/filter/find
    field_extractor: Optional[FieldPath] = None  # For sum/avg/max/min (the field to extract)
    location: Optional[SourceLocation] = None

    def is_predicate_function(self) -> bool:
        """Check if this is a predicate function (returns boolean)."""
        return self.function_type in (
            CollectionFunctionType.ANY,
            CollectionFunctionType.ALL,
            CollectionFunctionType.NONE
        )

    def is_aggregate_function(self) -> bool:
        """Check if this is an aggregate function (returns single value)."""
        return self.function_type in (
            CollectionFunctionType.SUM,
            CollectionFunctionType.COUNT,
            CollectionFunctionType.AVG,
            CollectionFunctionType.MAX,
            CollectionFunctionType.MIN
        )

    def is_transform_function(self) -> bool:
        """Check if this is a transform function (returns collection or element)."""
        return self.function_type in (
            CollectionFunctionType.FILTER,
            CollectionFunctionType.FIND,
            CollectionFunctionType.DISTINCT
        )
