import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="retail_db",
    user="postgres",
    password="Raji@0626",
    port="5432"
)

def get_orders(customer_id):

    cursor = conn.cursor()

    query = """
        SELECT *
        FROM orders
        WHERE customer_id = %s
    """

    try:
        cursor.execute(query, (customer_id,))
        results = cursor.fetchall()

        if customer_id == "1 OR 1=1":
            print(f"Injection input '{customer_id}' -> {len(results)} rows")
        else:
            print("Customer ID:", customer_id)
            print("Orders:", results)
            print("Number of rows:", len(results))

    except psycopg2.Error:
        conn.rollback()

        if customer_id == "1 OR 1=1":
            print(f"Injection input '{customer_id}' -> 0 rows")
        else:
            print("Invalid input rejected safely")

    finally:
        cursor.close()


# Normal customer input
get_orders(1)

# SQL injection test
get_orders("1 OR 1=1")

conn.close()