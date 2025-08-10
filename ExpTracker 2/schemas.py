from pydantic import BaseModel
import datetime

class ExpenseCreate(BaseModel):
    description: str
    amount: float
    category: str
    date_time: datetime.datetime

class ExpenseUpdate(ExpenseCreate):
    pass

class UserCreate(BaseModel):
    username: str
    password: str
