from fastapi import FastAPI
from .routers import register, login, song, likes

app = FastAPI()
app.include_router(register.router)
app.include_router(login.router)
app.include_router(song.router)
app.include_router(likes.router)


@app.get("/")
async def root():
    return {"message": "This is root"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
