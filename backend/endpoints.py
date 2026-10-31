import json
from time import monotonic

from auth import authenticate
from consts import WHITESPACE
from db import (
    FEED,
    GET_BY_ID,
    INSERT_LIKE,
    INSERT_POST,
    LIKE_EXISTS,
    POST_EXISTS,
    db,
)
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
    return JSONResponse(status_code=200, content={"status": "ok", "db": "ok", "uptime_s": int(monotonic() - request.state.up_time)})


# get latest 20 posts
async def get_posts(request: Request) -> JSONResponse:
    try:
        rows = db.execute(FEED).fetchall()
        return JSONResponse(status_code=200, content={"posts": [db_object(row) for row in rows]})
    except Exception as e:
        return ErrorResponse(status_code=400, content={"error": str(e)})


# get post by id
async def get_post(request: Request):
    try:
        id = parse_id(request.path_params["id"])
        row = db.execute(GET_BY_ID, (id,)).fetchone()

        if not id or not row:
            return ErrorResponse(status_code=404, content={"error": "post not found"})

        return JSONResponse(status_code=200, content={"post": db_object(row)})
    except TypeError as e:
        return ErrorResponse(status_code=400, content={"error": str(e)})


# create a post
@authenticate
async def create_post(request: FastRequest) -> JSONResponse | ErrorResponse:
    try:
        body = await request.json()
        if isinstance(body.get("body"), int) or not body:
            return ErrorResponse(status_code=400, content={"error": "body is required"})
        elif not body.get("body").strip():
            return ErrorResponse(status_code=400, content={"error": "body is required"})
        elif len(body["body"].strip(WHITESPACE)) > 500:
            return ErrorResponse(status_code=400, content={"error": "body must be at most 500 characters"})
    except json.JSONDecodeError:
        return ErrorResponse(status_code=400, content={"error": "malformed JSON body"})

    body = body["body"].strip(WHITESPACE)
    post_id, created_at = db.execute(INSERT_POST, (request.state.user_id, body)).fetchall()[0]
    return JSONResponse(
        status_code=201,
        content={"post": {
            "id": post_id,
            "body": body,
            "created_at": created_at,
            "author": request.state.username,
            "like_count": 0
        }}
    )


# like a post
@authenticate
async def create_like(request: Request) -> JSONResponse:
    try:
        post_id = parse_id(request.path_params["id"])
    except TypeError as e:
        return ErrorResponse(status_code=400, content={"error": str(e)})

    user_id = request.state["user_id"]
    post = db.execute(POST_EXISTS, (post_id,)).fetchone()
    like = db.execute(LIKE_EXISTS, (user_id, post_id)).fetchone()

    if post and not like:
        db.execute(INSERT_LIKE, (user_id, post_id))
        return JSONResponse(status_code=201, content={"liked": True, "already_liked": False, "post_id": post_id})

    if post and like:
        return JSONResponse(status_code=200, content={"liked": True, "already_liked": True, "post_id": post_id})

    if not post:
        return ErrorResponse(status_code=404, content={"error": "post not found"})
