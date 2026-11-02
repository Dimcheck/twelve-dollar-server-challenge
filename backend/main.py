from contextlib import asynccontextmanager
from time import monotonic

from endpoints import *
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware.exceptions import ExceptionMiddleware
from starlette.routing import Route


@asynccontextmanager
async def lifespan(app):
    print("Startup")
    yield {"up_time": monotonic()}
    print("Shutdown")


app = Starlette(
    debug=True,
    lifespan=lifespan,
    routes=[
        Route('/health', get_health),
        Route('/feed', get_posts),
        Route('/posts', create_post, methods=("POST",)),
        Route('/posts/{id}', get_post),
        Route('/posts/{id}/like', create_like, methods=("POST",)),
        Route('/', homepage),
    ],
)


async def not_found(request: Request, exc: HTTPException):
    """Custom response when user accesses non existent page"""
    return ErrorResponse(content={"error": "not found"}, status_code=exc.status_code)


exception_handlers = {404: not_found}


def slim_middleware_stack():
    """Custom middleware stack for faster request/response processing"""
    return ExceptionMiddleware(app.router, handlers=exception_handlers)


app.build_middleware_stack = slim_middleware_stack
