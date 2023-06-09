from .api import public
from .api import private
from .api import admin

import uvicorn
from fastapi import FastAPI
import os

from dotenv import load_dotenv
load_dotenv(os.environ.get("DOTENV_PATH", None))

app = FastAPI()

app.include_router(public.router)
app.include_router(private.router)
app.include_router(admin.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
