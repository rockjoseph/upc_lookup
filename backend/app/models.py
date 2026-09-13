"""Pydantic schemas shared across routers."""
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class QueryType(str, Enum):
    auto = "auto"
    url = "url"
    upc = "upc"
    keyword = "keyword"


class ProductLookupRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Product URL, UPC/barcode, or keyword")
    query_type: QueryType = QueryType.auto


class Product(BaseModel):
    sku: Optional[str] = None
    name: str
    original_price: Optional[float] = None
    sale_price: Optional[float] = None
    promo_deal: Optional[str] = None
    stock_status: Optional[str] = None
    url: str
    image_url: Optional[str] = None


class ProductCandidate(BaseModel):
    """A lightweight search-result entry when a keyword search is ambiguous."""

    name: str
    url: str
    image_url: Optional[str] = None


class ProductLookupResponse(BaseModel):
    product: Optional[Product] = None
    candidates: List[ProductCandidate] = Field(default_factory=list)
    message: Optional[str] = None


class ExcelRow(BaseModel):
    sku: Optional[str] = None
    name: str
    original_price: Optional[float] = None
    sale_price: Optional[float] = None
    promo_deal: Optional[str] = None
    last_checked: Optional[str] = None
    url: Optional[str] = None


class SessionResponse(BaseModel):
    session_id: str
    rows: List[ExcelRow]


class UpdateExcelRequest(BaseModel):
    session_id: str
    product: Product


class ErrorResponse(BaseModel):
    detail: str
