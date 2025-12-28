from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from app.api.routers import main_router
from app.core.middleware.cors import add_cors_middleware
from app.core.middleware.global_ import LoggingMiddleware

app = FastAPI(
    default_response_class=ORJSONResponse,
)

add_cors_middleware(app)
app.add_middleware(LoggingMiddleware)

app.include_router(main_router)
