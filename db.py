import sqlite3
import os
from dotenv import load_dotenv


load_dotenv()
# Caminho do banco de dados
db_path = os.getenv("DB_PATH")

# Função para criar a tabela no banco de dados, se não existir
def create_table():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS temperatures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()
        print("Tabela criada ou já existente.")
    except sqlite3.Error as e:
        print(f"Erro ao criar a tabela: {e}")
    finally:
        conn.close()

# Função para armazenar a temperatura no banco de dados
def store_temperature(temp):
    try:
        print("Armazenando a temperatura: ", temp)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO temperatures (temperature) VALUES (?)", (temp,))
        conn.commit()
        print("Temperatura armazenada com sucesso.")
    except sqlite3.Error as e:
        print(f"Erro ao armazenar a temperatura: {e}")
    finally:
        conn.close()