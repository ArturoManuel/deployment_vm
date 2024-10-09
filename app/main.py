from fastapi import FastAPI
from app.deployer.router import router

app = FastAPI()

# Incluir las rutas del router
app.include_router(router)
