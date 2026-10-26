from typing import Any

import orjson
from db import MAX_ID
from starlette.requests import Request
from starlette.responses import JSONResponse


class ErrorResponse(JSONResponse):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.status_code < 400:
            raise ValueError("Response is not an error")

    def __str__(self):
        return f"{self.__dict__}"


class FastRequest(Request):
    async def json(self) -> Any:
        if not hasattr(self, "_json"):  # pragma: no branch
            body = await self.body()
            self._json = orjson.loads(body)
        return self._json


def db_object(row: tuple) -> dict:
    return {"id": row[0], "body": row[1], "created_at": row[2], "author": row[3], "like_count": row[4]}


def parse_id(path_param: str) -> int:
    if path_param.isdigit():
        if int(path_param) > MAX_ID:
            raise ValueError("ID exceeds the DB limit")
        return path_param
    else:
        raise TypeError("Invalid ID")
