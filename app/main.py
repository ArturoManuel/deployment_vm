from fastapi import FastAPI,Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import PlainTextResponse
from app.deployer.router import router
from app.import_vms.route import modulo_import

app = FastAPI()

# Incluir las rutas del router
app.include_router(modulo_import)
app.include_router(router)


