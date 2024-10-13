import json
import os

import socket

# Función para leer archivos JSON en la carpeta 'slice_manager/datos'
def read_json_file(user_id: int, filename: str, action: str):
    """
    Lee un archivo JSON desde la carpeta slice_manager/data, añade un campo 'action' a las VMs
    con el valor proporcionado, y devuelve el JSON modificado.
    
    Args:
        user_id (int): El ID del usuario que está solicitando el archivo.
        filename (str): El nombre del archivo JSON.
        action (str): El valor de la acción ('crear', 'eliminar', 'info', etc.).
    
    Returns:
        dict: El JSON modificado con la acción aplicada a cada VM, o un error si ocurre algún problema.
    """
    # Ajustar la ruta para apuntar a la carpeta 'slice_manager/data'
    file_path = os.path.join('..', 'slice_manager', 'data', filename)  # Ruta relativa a slice_manager/data

    if not os.path.exists(file_path):
        return {"error": f"El archivo {filename} no existe en la carpeta slice_manager/datos."}

    try:
        # Leer el archivo JSON
        with open(file_path, "r") as f:
            data = json.load(f)  # Cargar el archivo JSON
            

            # Modificar el archivo JSON para agregar "action" con el valor proporcionado a cada VM
            for vm in data.get("vms", []):  # Iterar sobre las VMs si existen
                vm["action"] = action  # Añadir el campo 'action' con el valor que recibe la función

          
            # Devolver el JSON modificado
            return data

    except Exception as e:
        return {"error": f"Error al leer o modificar el archivo {filename}: {str(e)}"}
    

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
    results = []  # Almacena los resultados de cada worker

    for index, vm in enumerate(payload['vms']):
        worker_ip = workers_ips[index % num_workers]
        
        result = send_json_to_worker(worker_ip, vm)
        results.append({"worker_ip": worker_ip, "result": result})  # Guarda el resultado con la IP del worker
        
        if "Error" in result:
            return 500, results  # Devuelve inmediatamente con error y los resultados hasta ahora

    return 200, results  # Devuelve 200 si todo es exitoso, junto con todos los resultados





def request_system_stats(ip):
    try:
        # Conéctate al daemon de monitoreo en worker (puerto 9999)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, 9999))  # Reemplaza con la IP real de worker

        # Recibe la respuesta en formato JSON
        response = client_socket.recv(4096).decode()
        client_socket.close()

        return json.loads(response)
    
    except ConnectionRefusedError:
        return {"status": 400, "error": "No se pudo conectar al servidor de monitoreo."}
    except socket.timeout:
        return {"status": 500, "error": "El servidor no respondió a tiempo."}
    except Exception as e:
        return {"status": 500, "error": f"Error inesperado: {str(e)}"}

def format_stats(stats):
    # Verifica si el estado es 200, de lo contrario devuelve el mensaje de error
    if stats.get("status") != 200:
        return {
            "status": stats.get("status", 500),
            "error": stats.get("error", "Error desconocido")
        }

    # Formatea solo los datos relevantes cuando la respuesta es exitosa
    resources = stats.get("resources", {})
    uso_cpu = resources.get("cpu_usage", "N/D")
    info_memoria = resources.get("memory_info", {})
    uso_disco = resources.get("disk_usage", {})

    stats_formateadas = {
        "status": 200,
        "uso_cpu": f"{uso_cpu}%",  # Uso de CPU en porcentaje
        "memoria": {
            "total": f"{info_memoria.get('total', 'N/D') / (1024 ** 3):.2f} GB",
            "usada": f"{info_memoria.get('used', 'N/D') / (1024 ** 3):.2f} GB",
            "disponible": f"{info_memoria.get('available', 'N/D') / (1024 ** 3):.2f} GB",
            "porcentaje_usada": f"{info_memoria.get('percent', 'N/D')}%"
        },
        "disco": {
            "usado": f"{uso_disco.get('used', 'N/D') / (1024 ** 3):.2f} GB",
            "libre": f"{uso_disco.get('free', 'N/D') / (1024 ** 3):.2f} GB",
            "porcentaje_usado": f"{uso_disco.get('percent', 'N/D')}%"
        }
    }

    return stats_formateadas