from flask import Blueprint, request, jsonify
from config.db import get_db_connection

# crear el blueprint
tareas_bp = Blueprint('tareas', __name__)

# crear u endopoin obtener tareas


@tareas_bp.route('/obtener', methods=['GET'])
def get():
    return jsonify({"mensaje": "Estas son tus tareas"})

# crear endpoin con post recibiendo datos desde el body


@tareas_bp.route('/crear', methods=['POST'])
def crear():
    # datos del body
    data = request.get_json()
    descripcion = data.get('description')

    if not descripcion:
        return jsonify({"error": "debes tener una descripcion"}), 400

    # Obtenemos el cursor
    cursor = get_db_connection()

    # Hacemos el insert
    try:
        cursor.execute(
            'INSERT INTO tareas (descripcion) values (%s)', (descripcion,))
        cursor.connection.commit()
        return jsonify({"message": "tarea creada"}), 201
    except Exception as e:
        return jsonify({"Error": f"No se pudo crear la tarea: {str(e)}"}), 400
    finally:
        cursor.close()


@tareas_bp.route("/modificar/<int:user_id>", methods=["PUT"])
def modificar(user_id):
    data = request.get_json()

    nombre = data.get('nombre')
    apellido = data.get("apellido")

    mensaje = f"Usuario con id: {user_id} y nombre: {nombre} {apellido}"

    return jsonify({"saludo": mensaje})
