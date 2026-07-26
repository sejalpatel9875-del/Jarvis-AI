"""
Pydantic Data Transfer Objects for Document RAG endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class DocumentQueryRequest(BaseModel):
    query: str = Field(..., description="Semantic search query over document knowledge base", example="What is on page 17?")
    top_k: Optional[int] = Field(3, description="Number of top matching chunks to retrieve")
    filter_source: Optional[str] = Field(None, description="Optional filename filter e.g. invoice.pdf")
    filter_type: Optional[str] = Field(None, description="Optional document type filter e.g. pdf")

class DocumentChunkDTO(BaseModel):
    source_file: str
    page_number: int
    content: str
    score: float

class DocumentQueryResponse(BaseModel):
    query: str
    total_matches: int
    results: List[DocumentChunkDTO]
    formatted_answer: str
