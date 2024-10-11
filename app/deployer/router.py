from fastapi import APIRouter, Path , HTTPException, Path, status
from app.deployer.deployer import read_json_file ,deploy_vms_to_workers

# Crear el router para gestionar los endpoints
router = APIRouter()

# Endpoint para la topología de anillo
@router.get("/anillo/{user_id}")
async def anillo_topology(user_id: int = Path(..., description="ID del usuario")):
    return {"message": f"Hola mundo, soy anillo. El ID del usuario es {user_id}"}

# Endpoint para la topología lineal
@router.get("/lineal/{user_id}")
async def lineal_topology(user_id: int = Path(..., description="ID del usuario")):
    return {"message": f"Hola mundo, soy lineal. El ID del usuario es {user_id}"}


@router.get("/crear/{user_id}/{filename}", status_code=200)
async def get_topology_file(user_id: int, filename: str):
    action="crear"
    try:
        response = read_json_file(user_id, filename ,action )
        result_code = deploy_vms_to_workers(response)
        if result_code == 200:
            return {"message": "Despliegue completado con éxito"}
        else:
            raise HTTPException(status_code=500, detail="Error en el despliegue de VMs")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/eliminar/{user_id}/{filename}", status_code=200)
async def delete_vms(user_id: int, filename: str):
    action = "eliminar"
    try:
        # Leer el archivo con la acción de "eliminar"
        response = read_json_file(user_id, filename, action)

        # Ejecutar el despliegue o eliminación de VMs (suponiendo que 'deploy_vms_to_workers' lo maneje)
        result_code = deploy_vms_to_workers(response)

        if result_code == 200:
            return {"message": "Eliminación completada con éxito"}
        else:
            raise HTTPException(status_code=500, detail="Error en la eliminación de VMs")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/info/{user_id}/{filename}", status_code=200)
async def get_vm_info(user_id: int, filename: str):
    action = "info"
    try:
        # Leer el archivo con la acción de "info"
        response = read_json_file(user_id, filename, action)

        # Aquí no se ejecuta ninguna acción, solo retornamos la información
        return {"message": "Información de VMs obtenida con éxito", "data": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
