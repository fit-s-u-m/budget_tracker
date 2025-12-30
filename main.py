from fastapi import FastAPI
from api.route import create_app
from api.websocket import connect_websocket_app

app:FastAPI = create_app()
connect_websocket_app(app)
