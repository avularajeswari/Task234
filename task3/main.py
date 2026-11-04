from database import SessionLocal
from models import Customer, Product, Order
def setup_data():
    session = SessionLocal()

    try:
        customer = session.query(Customer).filter_by(id=1).first()

        if not customer:
            customer = Customer(
                id=1,
                name="Arun",
                city="Chennai",
                phone="9876543210"
            )
            session.add(customer)

        product = session.query(Product).filter_by(id=1).first()

        if not product:
            product = Product(
                id=1,
                name="Laptop",
                price=650,
                stock=10
            )
            session.add(product)

        session.commit()
        print("Sample data ready!")

    except Exception as e:
        session.rollback()
        print("Error:", e)

    finally:
        session.close()


def place_order(customer_id, product_id, qty, force_failure=False):

    session = SessionLocal()

    try:
        with session.begin():

            product = (
                session.query(Product)
                .filter_by(id=product_id)
                .with_for_update()
                .one_or_none()
            )

            if product is None:
                raise ValueError("Product not found")

            if product.stock < qty:
                raise ValueError("Insufficient stock")

            product.stock -= qty

            print("Stock updated:", product.stock)

            if force_failure:
                raise RuntimeError("Forced failure")

            order = Order(
                customer_id=customer_id,
                product_id=product_id,
                qty=qty,
                total_amount=product.price * qty
            )

            session.add(order)

        print("Order placed successfully!")

    except Exception as e:
        print("Transaction failed:", e)
        print("Rollback completed")

    finally:
        session.close()


def check_stock():

    session = SessionLocal()

    try:
        product = session.query(Product).filter_by(id=1).first()
        print("Current stock:", product.stock)

    finally:
        session.close()


if __name__ == "__main__":

    setup_data()

    print("\n--- Successful order ---")
    place_order(1, 1, 2)
    check_stock()

    print("\n--- Forced failure ---")

    # Reset stock to 10 for a separate rollback demonstration
    session = SessionLocal()
    try:
        product = session.query(Product).filter_by(id=1).first()
        product.stock = 10
        session.commit()
    finally:
        session.close()

    place_order(1, 1, 2, force_failure=True)
    check_stock()
