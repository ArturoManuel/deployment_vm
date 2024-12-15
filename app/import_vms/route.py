

from fastapi import APIRouter ,File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse

import aiofiles
import os
import logging

UPLOAD_DIRECTORY ='/home/ubuntu/images'
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)




logging.basicConfig(level=logging.DEBUG)
modulo_import=APIRouter()



@modulo_import.post("/upload-file/")
async def upload_file(file: UploadFile = File(...)):
    """
    Manejo de cargas grandes usando streams.
    """
    # Opcional: Validar tipos de archivos permitidos
    ALLOWED_CONTENT_TYPES = [
        "application/octet-stream",
        "application/x-iso9660-image",  # Tipo MIME para archivos .img
        "application/vnd.openstack.image",
        # Añade otros tipos si es necesario
    ]
    
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Tipo de archivo no permitido")
    
    file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
    
    try:
        async with aiofiles.open(file_path, "wb") as buffer:
            while True:
                content = await file.read(100*1024 * 1024)  # Leer en bloques de 1 MB
                if not content:
                    break
                await buffer.write(content)
                logging.debug(f"Escribiendo bloque de {len(content)} bytes")
        return {"filename": file.filename, "message": "Archivo cargado exitosamente"}
    except Exception as e:
        logging.error(f"Error al procesar el archivo: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail="Error al guardar el archivo")

