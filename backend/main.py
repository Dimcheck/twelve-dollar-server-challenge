from contextlib import asynccontextmanager
from time import monotonic

from endpoints import *
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.routing import Route


# Custom response when user accesses non existent page
async def not_found(request: Request, exc: HTTPException):
    return JSONResponse(content={"error": "not found"}, status_code=exc.status_code)

exception_handlers = {404: not_found}


@asynccontextmanager
async def lifespan(app):
    """
    Handle db connections
    Reuse 1 asynchronous HTTP client to communicate with External APIs
    Reuse 1 the ProcessPool to handle CPU heavy work
    ------------------------------------------------------------------
    https://starlette.dev/lifespan/
    """
    print("Startup")
    yield {"up_time": monotonic()}
    print("Shutdown")


app = Starlette(
    debug=True,
    lifespan=lifespan,
    exception_handlers=exception_handlers,
    routes=[
        Route('/health', get_health),
        Route('/feed', get_posts),
        Route('/posts', create_post, methods=("POST",)),
        Route('/posts/{id}', get_post),
        Route('/posts/{id}/like', create_like, methods=("POST",)),
        Route('/', homepage),
    ],
)
