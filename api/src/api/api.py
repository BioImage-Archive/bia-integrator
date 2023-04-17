from src.api import public
from src.api import private
from src.api import admin

from fastapi import FastAPI

app = FastAPI()

app.include_router(public.router)
app.include_router(private.router)
app.include_router(admin.router)
