from fastapi import FastAPI
from api.route import create_app

app:FastAPI = create_app()
