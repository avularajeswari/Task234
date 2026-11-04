import hmac
import hashlib

from fastapi import (
    FastAPI, Depends, HTTPException, Header, Query
)
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, ConfigDict

from app.database import Base, engine, get_db
from app.models import Customer
from app.auth import verify_api_key, WEBHOOK_SECRET

app = FastAPI(title="Secured Customer API")

Base.metadata.create_all(bind=engine)


class CustomerCreate(BaseModel):
    name: str
    email: EmailStr


class CustomerResponse(CustomerCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


# CREATE CUSTOMER
@app.post(
    "/customers",
    response_model=CustomerResponse,
    dependencies=[Depends(verify_api_key)]
)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(Customer).filter(
        Customer.email == customer.email
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Customer already exists"
        )

    new_customer = Customer(
        name=customer.name,
        email=customer.email
    )

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return new_customer


# GET CUSTOMERS WITH PAGINATION
@app.get(
    "/customers",
    dependencies=[Depends(verify_api_key)]
)
def get_customers(
    page: int = Query(1, ge=1),
    per_page: int = Query(5, ge=1, le=100),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * per_page

    customers = db.query(Customer).offset(
        offset
    ).limit(per_page).all()

    return {
        "page": page,
        "per_page": per_page,
        "customers": customers
    }


# GET CUSTOMER BY ID
@app.get(
    "/customers/{customer_id}",
    dependencies=[Depends(verify_api_key)]
)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    customer = db.query(Customer).filter(
        Customer.id == customer_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return customer


# UPDATE CUSTOMER
@app.put(
    "/customers/{customer_id}",
    dependencies=[Depends(verify_api_key)]
)
def update_customer(
    customer_id: int,
    data: CustomerCreate,
    db: Session = Depends(get_db)
):
    customer = db.query(Customer).filter(
        Customer.id == customer_id
    ).first()

    if not customer:
        raise HTTPException(404, "Customer not found")

    duplicate = db.query(Customer).filter(
        Customer.email == data.email,
        Customer.id != customer_id
    ).first()

    if duplicate:
        raise HTTPException(409, "Email already exists")

    customer.name = data.name
    customer.email = data.email

    db.commit()
    db.refresh(customer)

    return customer


# DELETE CUSTOMER
@app.delete(
    "/customers/{customer_id}",
    dependencies=[Depends(verify_api_key)]
)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    customer = db.query(Customer).filter(
        Customer.id == customer_id
    ).first()

    if not customer:
        raise HTTPException(404, "Customer not found")

    db.delete(customer)
    db.commit()

    return {"message": "Customer deleted successfully"}


# WEBHOOK WITH HMAC-SHA256
@app.post("/webhooks/order-events")
async def order_webhook(
    payload: dict,
    x_signature: str = Header(default=None)
):
    import json

    if not x_signature:
        raise HTTPException(401, "Missing signature")

    body = json.dumps(
        payload,
        separators=(",", ":"),
        ensure_ascii=False
    ).encode()

    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(
        expected_signature,
        x_signature
    ):
        raise HTTPException(401, "Invalid signature")

    return {"message": "Webhook accepted"}