from pydantic import BaseModel
from typing import List, Dict, Any

class KPISchema(BaseModel):
    total_products: int
    total_reviews: int
    average_rating: float
    number_of_categories: int

class ChartDataPoint(BaseModel):
    label: str
    value: Any

class DashboardDataResponse(BaseModel):
    kpi: KPISchema
    products_by_category: List[Dict[str, Any]]
    products_by_brand: List[Dict[str, Any]]
    price_distribution: List[float]
    rating_distribution: List[float]
    review_rating_distribution: List[float]
    recommendation_status: List[Dict[str, Any]]
    buyer_status: List[Dict[str, Any]]
    price_vs_rating: List[Dict[str, Any]]
    insights: List[Dict[str, str]]
