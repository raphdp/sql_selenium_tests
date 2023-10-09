# init.py
import mysql.connector

def create_table_if_not_exists():
    conn = mysql.connector.connect(
        host="mysql",  # the name of the MySQL service in Docker Compose
        user="user",
        password="password",
        database="testdb"
    )
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS composition (
            Name VARCHAR(255),
            Quantité FLOAT,
            PRU FLOAT,
            Cours FLOAT,
            Valo FLOAT,
            `+/-Val` FLOAT,
            `var/PRU` FLOAT,
            `var/Veille` FLOAT,
            `%` FLOAT,
            `Ordre Limite` FLOAT,
            Total FLOAT,
            Currency VARCHAR(255),
            `Time of Update` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_table_if_not_exists()