from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from models import User, Expense
from schemas import UserCreate, ExpenseCreate, ExpenseUpdate

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    new_user = User(username=user.username, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully", "user_id": new_user.id}

@app.post("/expenses/")
def add_expense(expense: ExpenseCreate, user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    new_expense = Expense(
        description=expense.description,
        amount=expense.amount,
        category=expense.category,
        date_time=expense.date_time,
        owner=user
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return {"message": "Expense added successfully", "expense_id": new_expense.id}

@app.get("/expenses/")
def get_expenses(user_id: int, db: Session = Depends(get_db)):
    expenses = db.query(Expense).filter(Expense.user_id == user_id).all()
    return expenses

@app.put("/expenses/{expense_id}")
def update_expense(expense_id: int, expense: ExpenseUpdate, db: Session = Depends(get_db)):
    db_expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    for key, value in expense.dict().items():
        setattr(db_expense, key, value)
    db.commit()
    db.refresh(db_expense)
    return {"message": "Expense updated successfully"}

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(expense)
    db.commit()
    return {"message": "Expense deleted successfully"}
