from flask_mysqldb import MySQL
import os
from dotenv import load_dotenv

# Cargar de .env las variables
load_dotenv()

# Instancia de SQL
mysql = MySQL()


def init_db(app):
    """DATABASE CONFIG CON LA INSTANCIA DE FLASK"""
    app.config['MYSQL_HOST'] = os.getenv("DB_HOST")
    app.config['MYSQL_USER'] = os.getenv("DB_USER")
    app.config['MYSQL_PASSWORD'] = os.getenv("DB_PASSWORD")
    app.config['MYSQL_DB'] = os.getenv("DB_NAME")
    app.config['MYSQL_PORT'] = int(os.getenv("DB_PORT"))

    # Inicializamos la conexión
    mysql.init_app(app)

# Definimos  el cursor


def get_db_connection():
    """devuelve el cursor para interactuar con la bd"""
    try:
        connection = mysql.connection
        return connection.cursor()
    except Exception as e:
        raise RuntimeError(f"Error a la base de datos: {e}")
