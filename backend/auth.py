import base64
import hashlib
import hmac
import os
from collections.abc import Callable, Coroutine
from functools import cached_property, wraps
from time import time

import orjson
from starlette.requests import Request
from utils import ErrorResponse

MAX_ID = 2**63 - 1  # SQLite's INTEGER range; larger ids cannot exist
JWT_SECRET = os.environ["JWT_SECRET"].encode()


class JWT:
    """
    JWT typically looks like the following:
        xxxxx.yyyyy.zzzzz
    Header
        The header typically consists of two parts: the type of the token, which is JWT, and the signing algorithm being used, such as HMAC SHA256 or RSA.
    Payload
        The second part of the token is the payload, which contains the claims. Claims are statements about an entity (typically, the user) and additional data.
    Signature
        To create the signature part you have to take the encoded header, the encoded payload, a secret, the algorithm specified in the header, and sign that.

    NOTE: Base64URL alphabet consists entirely of ASCII characters, so .encode("ascii")/.decode("ascii") is mandatory
    """

    alg = "HS256"
    typ = "JWT"
    token: str = None

    def __init__(self, **kwargs) -> None:
        payload = self._create_payload(**kwargs)
        signature = self._create_signature(f"{self._header}.{payload}".encode("ascii"))
        self.token = f"{self._header}.{payload}.{signature}"

    @cached_property
    def _header(self) -> str:
        header = {"alg": self.alg, "typ": self.typ}
        return base64.urlsafe_b64encode(orjson.dumps(header)).rstrip(b"=").decode("ascii")

    @staticmethod
    def _create_payload(**kwargs) -> str:
        try:
            payload = {"sub": kwargs["sub"], "username": kwargs["username"], "iat": int(time()), "exp": int(time()+3600)}
            return base64.urlsafe_b64encode(orjson.dumps(payload)).rstrip(b"=").decode("ascii")
        except KeyError as e:
            print(f"{e} is missing")
            raise KeyError

    @staticmethod
    def _create_signature(signing_input: bytes) -> str:
        digest = hmac.new(key=JWT_SECRET, msg=signing_input, digestmod=hashlib.sha256).digest()
        return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")

    def __str__(self):
        return self.token


def authenticate(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs) -> Coroutine:
        header = request.headers.get("authorization")
        if header is None or not header.startswith("Bearer "):
            return ErrorResponse(status_code=401, content={"error": "missing bearer token"})

        try:
            head_b64, payload_b64, sig_b64 = header[7:].split(".")
            # add padding back to head_b64 before decoding
            head = orjson.loads(base64.urlsafe_b64decode(head_b64 + "=" * (-len(head_b64) % 4)))
            if not isinstance(head, dict) or head.get("alg") != "HS256":
                raise ValueError("alg")

            signature = JWT._create_signature(f"{head_b64}.{payload_b64}".encode("ascii"))
            if not hmac.compare_digest(signature, sig_b64):
                raise ValueError("signature")

            # add padding back to payload_b64 before decoding
            payload = orjson.loads(base64.urlsafe_b64decode(payload_b64 + "=" * (-len(payload_b64) % 4)))
            if not isinstance(payload, dict):
                raise ValueError("payload")
            now = int(time())
            exp = payload.get("exp")
            if exp is not None and (not isinstance(exp, (int, float)) or isinstance(exp, bool) or now >= exp):
                raise ValueError("exp")
            # nbf = payload.get("nbf")
            # if nbf is not None and (not isinstance(nbf, (int, float)) or isinstance(nbf, bool) or now < nbf):
                # raise ValueError("nbf")
        except (ValueError, UnicodeError) as e:  # includes orjson.JSONDecodeError and binascii.Error
            print(e.__dict__)
            return ErrorResponse(status_code=401, content={"error": "invalid or expired token"})
        sub = payload.get("sub")
        username = payload.get("username")
        user_id = int(sub) if isinstance(sub, str) and sub.isdigit() else None

        if user_id is None or user_id > MAX_ID or not isinstance(username, str):
            return ErrorResponse(status_code=401, content={"error": "invalid token payload"})

        # Attach authenticated user info to request for the endpoint function
        request.state.user_id = user_id
        request.state.username = username

        return await func(request, *args, **kwargs)
    return wrapper
