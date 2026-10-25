from auth import authenticate
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from utils import ErrorResponse


# root
async def homepage(request: Request):
    return JSONResponse({'data': 'welcome'})


# health check
async def get_health(request: Request):
    ...


# get latest 20 posts
async def get_posts(request: Request):
    ...


# get post by id
async def get_post(request: Request):
    ...


# create a post (auth)
@authenticate
async def create_post(request: Request) -> Response | ErrorResponse:
    print(request.state.__dict__)
    return Response(content="Success", status_code=201)


# like a post (auth)
@authenticate
async def create_like(request: Request):
    ...