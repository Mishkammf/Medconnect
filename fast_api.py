import uvicorn
from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import JSONResponse

from apimodel.response_models import APIError
from common.config_manager import get_config
from exceptions.custom_exceptions import CustomAPIException
from init import COMMON_API_PREFIX, static_path
from router import user, token, \
    session, transferrequest, hospital, ambulancerequest

app = FastAPI(
    title="Medconnect API",
    version="1.0.0",
    description="Medconnect API documentation"
)

app.mount(f'/{static_path}', StaticFiles(directory=static_path), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.exception_handler(CustomAPIException)
async def custom_exception_handler(request: Request, exception: CustomAPIException):
    return JSONResponse(
        status_code=exception.status_code if hasattr(exception, "status_code") else status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(APIError(type=exception.name, message=exception.message))
    )


app.include_router(token.router, prefix=f"{COMMON_API_PREFIX}/token", tags=["Token"])
app.include_router(session.router, prefix=f"{COMMON_API_PREFIX}/session", tags=["Session"])
app.include_router(user.router, prefix=f"{COMMON_API_PREFIX}/users", tags=["Users"])
app.include_router(hospital.router, prefix=f"{COMMON_API_PREFIX}/hospitals", tags=["Hospitals"])
app.include_router(transferrequest.router, prefix=f"{COMMON_API_PREFIX}/transferrequest", tags=["TransferRequests"])
app.include_router(ambulancerequest.router, prefix=f"{COMMON_API_PREFIX}/ambulancerequest", tags=["AmbulanceRequests"])
if __name__ == "__main__":
    uvicorn.run("fast_api:app", host="0.0.0.0", port=get_config("api_host_port"), reload=True)
