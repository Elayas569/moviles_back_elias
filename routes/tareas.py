from flask import Blueprint, request, jsonify
from config.db import get_db_connection
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt, get_jwt_identity
from flask_bcrypt import bcrypt, Bcrypt
from config.db import get_db_connection

# crear el blueprint
tareas_bp = Blueprint('tareas', __name__)

# crear u endopoin obtener tareas


@tareas_bp.route('/obtener', methods=['GET'])
@jwt_required()
def get():

    current_user = get_jwt_identity()
    cursor = get_db_connection()

    querry = '''
                SELECT a.id_usuario, a.descripcion, b.nombre, b.email, a.creado_en
                FROM tareas as a
                INNER JOIN usuarios as b on a.id_usuario = b.id_usuario
                WHERE a.id_usuario = %s
            '''
    cursor.execute(querry, (current_user,))
    lista = cursor.fetchall()
    cursor.close()

    if not lista:
        return jsonify({"Error": "El usuario no tiene tareas"}), 404
    else:
        return jsonify({"Lista": lista}), 200


# crear endpoin con post recibiendo datos desde el body


@tareas_bp.route('/crear', methods=['POST'])
@jwt_required()
def crear():
    # datos del body

    current_user = get_jwt_identity()

    data = request.get_json()
    descripcion = data.get('description')

    if not descripcion:
        return jsonify({"error": "debes tener una descripcion"}), 400

    # Obtenemos el cursor
    cursor = get_db_connection()

    # Hacemos el insert
    try:
        cursor.execute(
            'INSERT INTO tareas (descripcion, id_usuario) values (%s, %s)', (descripcion, current_user))
        cursor.connection.commit()
        return jsonify({"message": "tarea creada"}), 201
    except Exception as e:
        return jsonify({"Error": f"No se pudo crear la tarea: {str(e)}"}), 400
    finally:
        cursor.close()


@tareas_bp.route("/modificar/<int:id_tarea>", methods=["PUT"])
@jwt_required()
def modificar(id_tarea):

    current_user = get_jwt_identity()
    cursor = get_db_connection()
    descripcion = request.get_json()

    # Checar que la tarea
    querry = "SELECT * FROM tareas WHERE id_tarea = %s"
    cursor.execute(querry, (id_tarea,))
    tarea = cursor.fetchone()

    if not tarea:
        cursor.close()
        return jsonify({"Error": "Esa tarea no existe"}), 404

    if not tarea[1] == int(current_user):
        cursor.close()
        return jsonify({"Error": "Credenciales Incorrectas"}), 401

    # Actualizar datos
    try:
        cursor.execute(
            "UPDATE tareas SET descripcion = %s WHERE id_tarea = %s", (descripcion, id_tarea))
        cursor.connection.commit()
        return jsonify({"Mensaje": "Datos actualizados correctamente"}), 200
    except Exception as e:
        return jsonify({"Error": f"Error en la base {e}"}), 400

    finally:
        cursor.close()
