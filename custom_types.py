from pydantic import BaseModel
from typing import Literal, Optional

class TransactionRequest(BaseModel):
    account_id: int
    amount: int
    category: str
    reason: Optional[str] = None
    type_:Literal["credit", "debit"] = "debit"

