from pydantic import BaseModel, Field
from typing import List, Optional

class AttributeAnalysis(BaseModel):
    """
    Defines the structural constraint map for an isolated 
    data dictionary attribute row returned from inference.
    """
    attribute_name: str = Field(
        ..., 
        description="The exact name of the raw field column matching user dataset casing profiles."
    )
    provisional_entity: Optional[str] = Field(
        None, 
        description="The guessed logical root group class or system context prefix."
    )
    is_geographical: bool = Field(
        ..., 
        description="True if the property denotes structural geospatial tracking layout indices."
    )
    related_entity: Optional[str] = Field(
        None, 
        description="The explicit component entity link binding the attribute down to structural groups."
    )
    provisional_python_type: str = Field(
        ..., 
        description="The native primitive structure parsing rule type (e.g. str, int, float, bool)."
    )

class BatchAnalysisResponse(BaseModel):
    """
    Validates structural bulk payload JSON maps returned 
    from the local Ollama structural matrix engine.
    """
    analysis: List[AttributeAnalysis] = Field(
        ..., 
        description="A sequential collection tracking mapped dictionary data elements."
    )
