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


@router.get("/topologia/{user_id}/{filename}", status_code=200)
async def get_topology_file(user_id: int, filename: str):
    try:
        response = read_json_file(user_id, filename)
        result_code = deploy_vms_to_workers(response)

        if result_code == 200:
            return {"message": "Despliegue completado con éxito"}
        else:
            raise HTTPException(status_code=500, detail="Error en el despliegue de VMs")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
