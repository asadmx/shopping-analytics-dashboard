import os
import pandas as pd
from sqlalchemy import text
from app.db import get_engine

TABLE_SQL = """
CREATE TABLE IF NOT EXISTS orders (
  order_id        INT PRIMARY KEY,
  order_date      DATE NOT NULL,
  customer_id     TEXT NOT NULL,
  gender          TEXT,
  age             INT,
  category        TEXT,
  item            TEXT,
  quantity        INT NOT NULL,
  price           NUMERIC(10,2) NOT NULL,
  discount_pct    NUMERIC(5,2) NOT NULL,
  shipping_type   TEXT,
  subscription    TEXT
);
"""

def main():
    csv_path = os.path.join("data", "sample.csv")
    df = pd.read_csv(csv_path)
    df["order_date"] = pd.to_datetime(df["order_date"]).dt.date

    eng = get_engine()
    with eng.begin() as conn:
        conn.execute(text(TABLE_SQL))
        conn.execute(text("DELETE FROM orders;"))
        df.to_sql("orders", conn, if_exists="append", index=False)

    print("Loaded sample data into Postgres table: orders")

if __name__ == "__main__":
    main()
