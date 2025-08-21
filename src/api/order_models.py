from pydantic import BaseModel, ConfigDict


class LimitLimitGtc(BaseModel):
    model_config = ConfigDict(extra="ignore")

    quote_size: str
    base_size: str
    limit_price: str
    post_only: bool


class OrderConfiguration(BaseModel):
    model_config = ConfigDict(extra="ignore")

    limit_limit_gtc: LimitLimitGtc


class Order(BaseModel):
    model_config = ConfigDict(extra="ignore")

    order_id: str
    product_id: str
    user_id: str
    order_configuration: OrderConfiguration
    side: str
    client_order_id: str
    status: str


class SuccessResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    order_id: str
    product_id: str
    side: str
    client_order_id: str


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    error: str
    message: str
    error_details: str
    preview_failure_reason: str
    new_order_failure_reason: str


class OrderReceipt(BaseModel):
    model_config = ConfigDict(extra="ignore")

    success: bool
    success_response: SuccessResponse
    error_response: ErrorResponse
    order_configuration: OrderConfiguration
