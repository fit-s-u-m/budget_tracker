from pydantic import BaseModel
from typing import Literal, Optional
from enum import Enum, auto

class TransactionRequest(BaseModel):
    account_id: int
    amount: int
    category: str
    reason: Optional[str] = None
    type_:Literal["credit", "debit"] = "debit"


class State(Enum):
    START = auto()
    TYPE = auto()
    AMOUNT = auto()
    REASON = auto()
