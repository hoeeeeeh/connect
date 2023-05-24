from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import calculation

app = FastAPI()
origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(calculation.router)


@app.get("/")
async def main():
    print("success")
    return {"main": "success"}
