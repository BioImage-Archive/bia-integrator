from .api import public
from .api import private
from .api import admin

import uvicorn
from fastapi import FastAPI

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

app.include_router(public.router)
app.include_router(private.router)
app.include_router(admin.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
