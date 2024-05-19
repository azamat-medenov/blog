import uvicorn
from fastapi import FastAPI


def main() -> FastAPI:
    app = FastAPI()

    return app


def run() -> None:
    uvicorn.run(r"main:main", reload=True, port=8000)


if __name__ == "__main__":
    run()
