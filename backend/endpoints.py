import json

from auth import authenticate
from db import FEED, GET_BY_ID, INSERT, db
from starlette.requests import Request
from starlette.responses import JSONResponse
from utils import ErrorResponse, FastRequest, db_object, parse_id


async def homepage(request: Request) -> JSONResponse:
    return JSONResponse({'data': 'welcome'})


# health check
async def get_health(request: Request):
    try:
        db.execute("SELECT 1").fetchone()
    except Exception as e:
        return ErrorResponse(status_code=503, content={"status": "degraded", "db": "unreachable", "error": str(e)})
    return JSONResponse(status_code=200, content={"status": "ok", "db": "ok"})


# get latest 20 posts
async def get_posts(request: Request) -> JSONResponse:
    rows = db.execute(FEED).fetchall()
    return JSONResponse(status_code=200, content={"posts": [db_object(row) for row in rows]})


# get post by id
async def get_post(request: Request):
    try:
        row = db.execute(GET_BY_ID, (parse_id(request.path_params["id"]))).fetchone()
    except Exception as e:
        return ErrorResponse(status_code=400, content={"error": str(e)})
    return JSONResponse(status_code=200, content={"post": db_object(row)})


# create a post (auth)
@authenticate
async def create_post(request: FastRequest) -> JSONResponse | ErrorResponse:
    try:
        body = await request.json()

        if isinstance(body.get("body"), int) or not body:
            return ErrorResponse(status_code=400, content={"error": "body is required"})
        elif not body.get("body").strip():
            return ErrorResponse(status_code=400, content={"error": "body is required"})
        elif len(body["body"]) > 500:
            return ErrorResponse(status_code=400, content={"error": "body must be at most 500 characters"})
    except json.JSONDecodeError:
        return ErrorResponse(status_code=400, content={"error": "malformed JSON body"})

    db.execute(INSERT, (request.state.user_id, body["body"]))
    return JSONResponse(status_code=201, content=await request.json())


# like a post (auth)
@authenticate
async def create_like(request: Request) -> JSONResponse:
    print(request.state.__dict__)
    return JSONResponse(status_code=201, content="Success")
