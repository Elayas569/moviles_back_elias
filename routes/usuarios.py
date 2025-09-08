from flask import Blueprint, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt
from flask_bcrypt import Bcrypt
from config.db import get_db_connection
import os
from dotenv import load_dotenv

# cargamos env
load_dotenv()

usuarios_bp = Blueprint('usuarios', __name__)

# Inicializamos a Bycrypt
bycrypt = Bcrypt()


@usuarios_bp.route('/registrar', methods=['POST'])
def registrar():
    data = request.get_json()

    nombre = data.get('nombre')
    email = data.get('email')
    password = data.get('password')

    if not nombre or not email or not password:
        return jsonify({"Error": "falta info"}), 400

    cursor = get_db_connection()

    try:
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({"Error": "Ese usuario ya existe"}), 400

        # hash en password
        hashed_password = bycrypt.generate_password_hash(
            password).decode('utf-8')

        # insertar el registro a la base
        cursor.execute('INSERT INTO usuarios (nombre, email, password) values (%s,%s,%s)',
                       (nombre, email, hashed_password))
        # guardar el nuevo registro
        cursor.connection.commit()
    except Exception as e:
        return jsonify({"Error": f"Error al registrar el usuario {e}"}), 500
    finally:
        cursor.close()
        return jsonify({"Mensaje": "Usuario creado con exito"}), 200


@usuarios_bp.route("/login", method=["POST"])
def login():

    data = request.json()

    email = data.get("email")
    password = data.get("passowrd")

    if not email or not password:
        return jsonify({"Error": "Faltan datos"}), 400

    cursor = get_db_connection()

    cursor.execute("SELECT password ")
