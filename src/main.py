from fastapi import FastAPI
from api.v1 import router as v1_router


app = FastAPI()

app.include_router(v1_router, prefix="/api/v1")




if __name__ == "__main__":
    # only for development
    import webbrowser
    import uvicorn

    port = 8080
    uvicorn.run("main:app", port=port, reload=True)