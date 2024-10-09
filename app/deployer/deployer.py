import json
import os

import socket

# Función para leer archivos JSON en la carpeta 'slice_manager/datos'
def read_json_file(user_id: int, filename: str):
    # Ajustar la ruta para apuntar a la carpeta 'slice_manager/datos'
    file_path = os.path.join('..', 'slice_manager', 'data', filename)  # Ruta relativa a slice_manager/datos

    if not os.path.exists(file_path):
        return {"error": f"El archivo {filename} no existe en la carpeta slice_manager/datos."}

    try:
        with open(file_path, "r") as f:
            data = json.load(f)  # Leer el archivo JSON
            print(f"Contenido del archivo {filename}: {data}")  # Imprimir el contenido
            return data  # Devolver el contenido como respuesta
    except Exception as e:
        return {"error": f"Error al leer el archivo {filename}: {str(e)}"}


def send_json_to_worker(ip_worker, data):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip_worker, 9998))
        json_data = json.dumps(data)
        client_socket.send(json_data.encode())

        result = client_socket.recv(4096).decode()
        client_socket.close()
        return result
    except Exception as e:
        return f"Error: {str(e)}"  # Devuelve el mensaje de error si ocurre uno

def deploy_vms_to_workers(payload):
    workers_ips = ['10.0.0.30', '10.0.0.40', '10.0.0.50']
    num_workers = len(workers_ips)
    success = True  # Asume inicialmente que todo es exitoso

    for index, vm in enumerate(payload['vms']):
        worker_ip = workers_ips[index % num_workers]
        print(f"Enviando {vm['name']} al worker con IP {worker_ip}")

        result = send_json_to_worker(worker_ip, vm)
        print(f"Resultado del despliegue en {worker_ip}: {result}")

        if "Error" in result:
            success = False  # Cambia a falso si algún worker reporta un error

    return 200 if success else 500  # Devuelve 200 si todo es exitoso, de lo contrario 500