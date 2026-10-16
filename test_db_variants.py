import psycopg2
import os

users_to_try = [("postgres", "postgres"), ("postgres", ""), ("postgres", "postgres"), ("muhammad", "muhammad"), ("muhammad", "")]

for user, pwd in users_to_try:
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user=user,
            password=pwd,
            dbname="digikala_db",
            connect_timeout=2
        )
        conn.close()
        print(f"SUCCESS with DB_USER={user}, DB_PASSWORD={pwd}")
        break
    except Exception as e:
        print(f"Failed with user={user}, pwd={pwd}: {e}")
