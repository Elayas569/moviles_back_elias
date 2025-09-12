from flask import Blueprint, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt, get_jwt_identity
from flask_bcrypt import bcrypt, Bcrypt
from config.db import get_db_connection
import os
from dotenv import load_dotenv
import datetime

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


@usuarios_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"Error": "Faltan datos"}), 400

    cursor = get_db_connection()

    querry = ("SELECT password, id_usuario FROM usuarios WHERE email = %s")
    cursor.execute(querry, (email,))

    usuario = cursor.fetchone()

    if usuario and bycrypt.check_password_hash(usuario[0], password):
        # genera mos jwt
        expires = datetime.timedelta(minutes=60)

        access_token = create_access_token(
            identity=str(usuario[1]),
            expires_delta=expires
        )
        cursor.close()

        return jsonify({"token": access_token}), 200
    else:
        return jsonify({"Error": "Credenciales incorrectas"}), 401


@usuarios_bp.route("/datos", methods=["GET"])
@jwt_required()
def datos():
    current_user = get_jwt_identity()
    cursor = get_db_connection()

    querry = "SELECT id_usuario, nombre, email FROM USUARIOS where id_usuario = %s"
    cursor.execute(querry, (current_user,))
    usuario = cursor.fetchone()

    cursor.close()

    if usuario:
        user_info = {
            "id_usuario": usuario[0],
            "nombre": usuario[1],
            "email": usuario[2],
        }
        return jsonify({"Datos": user_info}), 200
    else:
        return jsonify({"Error": "Usuario no encontrado"}), 404
