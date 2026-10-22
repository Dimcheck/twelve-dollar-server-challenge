import base64
import hashlib
import hmac
import os
import time

import orjson
from starlette.requests import Request
from starlette.responses import Response

JWT_SECRET = os.environ["JWT_SECRET"].encode()
# Implement a JWT authentication from scratch using imported modules...
