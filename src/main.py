from fastapi import FastAPI

from core.configs.application_config import application_config
from core.exceptions.api_exceptions import BaseAPIException
from core.exceptions.handlers import base_api_exception_handler, global_exception_handler
from api.v1 import router as v1_router

app = FastAPI()

app.include_router(v1_router, prefix="/api/v1")
app.add_exception_handler(BaseAPIException, base_api_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)


if __name__ == "__main__":
    # only for development
    import webbrowser
    import uvicorn

    port = application_config.PORT

    if application_config.ENV == "DEV":
        webbrowser.open_new(f"http://localhost:{port}/docs")
        
    uvicorn.run("main:app", port=port, reload=True)