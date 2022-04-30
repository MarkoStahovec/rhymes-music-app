from fastapi import FastAPI
from .routers import register, login, song

app = FastAPI()
app.include_router(register.router)
app.include_router(login.router)
app.include_router(song.router)


@app.get("/")
async def root():
    return {"message": "This is root"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
