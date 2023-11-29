import psycopg2

params = {
    'database': 'postgres',
    'user': 'postgres',
    'password': 'mysecretpassword',
    'host': 'localhost',
    'port': 5432
}

conn = psycopg2.connect(**params)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS cars (
    id SERIAL PRIMARY KEY,
    description VARCHAR(500),
    prices VARCHAR(200)
)
""")
#
# cur.execute("""
#     DROP TABLE cars
# """)

conn.commit()

cur.close()
conn.close()
