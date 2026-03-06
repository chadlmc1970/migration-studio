"""CIM File Loader"""
import json
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class CIMTable(BaseModel):
    name: str
    alias: Optional[str] = None


class CIMJoin(BaseModel):
    left_table: str
    right_table: str
    type: str = "inner"
    condition: str


class CIMDimension(BaseModel):
    name: str
    table: str
    column: str
    description: Optional[str] = None


class CIMMeasure(BaseModel):
    name: str
    table: str
    column: str
    aggregation: str = "SUM"
    description: Optional[str] = None


class CIMUniverse(BaseModel):
    name: str
    id: str


class CIMModel(BaseModel):
    schema_version: str
    universe: CIMUniverse
    tables: list[CIMTable] = Field(default_factory=list)
    joins: list[CIMJoin] = Field(default_factory=list)
    dimensions: list[CIMDimension] = Field(default_factory=list)
    measures: list[CIMMeasure] = Field(default_factory=list)


def load_cim(file_path: Path) -> CIMModel:
    """Load and parse a CIM JSON file"""
    with open(file_path, 'r') as f:
        data = json.load(f)

    # Handle both old CIMModel format and new CanonicalModel format
    if 'business_layer' in data:
        # New CanonicalModel format from parser
        bl = data.get('business_layer', {})
        df = data.get('data_foundation', {})

        # Convert to CIMModel format
        return CIMModel(
            schema_version=data.get('schema_version', '0.1'),
            universe=CIMUniverse(
                name=data.get('universe_name', ''),
                id=data.get('universe_id', '')
            ),
            tables=[CIMTable(name=t) for t in df.get('tables', [])],
            joins=[CIMJoin(**j) for j in df.get('joins', [])],
            dimensions=[CIMDimension(**d) for d in bl.get('dimensions', [])],
            measures=[CIMMeasure(**m) for m in bl.get('measures', [])]
        )
    else:
        # Old CIMModel format
        return CIMModel(**data)


def scan_cim_directory(cim_dir: Path) -> list[Path]:
    """Scan directory for CIM files"""
    return list(cim_dir.glob("*.cim.json"))


def generate_mock_cim(output_path: Path) -> CIMModel:
    """Generate a mock CIM file for testing"""
    mock = CIMModel(
        schema_version="0.1",
        universe=CIMUniverse(name="Sales", id="sales_universe"),
        tables=[
            CIMTable(name="ORDERS"),
            CIMTable(name="CUSTOMERS"),
            CIMTable(name="PRODUCTS")
        ],
        joins=[
            CIMJoin(
                left_table="ORDERS",
                right_table="CUSTOMERS",
                type="inner",
                condition="ORDERS.CUST_ID = CUSTOMERS.ID"
            ),
            CIMJoin(
                left_table="ORDERS",
                right_table="PRODUCTS",
                type="inner",
                condition="ORDERS.PROD_ID = PRODUCTS.ID"
            )
        ],
        dimensions=[
            CIMDimension(name="Customer Name", table="CUSTOMERS", column="NAME"),
            CIMDimension(name="Product Name", table="PRODUCTS", column="NAME"),
            CIMDimension(name="Order Date", table="ORDERS", column="ORDER_DATE")
        ],
        measures=[
            CIMMeasure(name="Revenue", table="ORDERS", column="AMOUNT", aggregation="SUM"),
            CIMMeasure(name="Quantity", table="ORDERS", column="QTY", aggregation="SUM"),
            CIMMeasure(name="Order Count", table="ORDERS", column="ID", aggregation="COUNT")
        ]
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(mock.model_dump(), f, indent=2)

    return mock
