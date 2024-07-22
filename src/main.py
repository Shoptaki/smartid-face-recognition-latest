from fastapi import FastAPI
from src.routes import example_routes

app = FastAPI()

app.include_router(example_routes.router)