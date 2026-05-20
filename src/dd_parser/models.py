from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class AttributeAnalysis(BaseModel):
    attribute_name: str
    provisional_entity: str = Field(
        description="The primary business entity this attribute belongs to (e.g., Customer, Product, Transaction)."
    )
    is_geographical: bool = Field(
        description="True if the attribute represents a physical location, address, coordinate, country, or region."
    )
    related_entity: Optional[str] = Field(
        None, 
        description="If geographical, which entity does this location bind to? (e.g., 'Customer' for 'shipping_state')."
    )
    provisional_python_type: Literal["str", "int", "float", "datetime.date", "datetime.datetime", "bool"] = Field(
        description="Semantic Python data type based on semantics."
    )

class BatchAnalysisResponse(BaseModel):
    analysis: List[AttributeAnalysis]
