from contextlib import asynccontextmanager

from endpoints import *
from starlette.applications import Starlette
from starlette.routing import Route


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
    yield
    print("Shutdown")


app = Starlette(
    debug=True,
    lifespan=lifespan,
    routes=[
        Route('/health', get_health),
        Route('/feed', get_posts),
        Route('/posts', create_post),
        Route('/posts/:id', get_post),
        Route('/posts/:id/like', create_like),
        Route('/', homepage),
    ]
)
