import os

SQLITE_PATH = os.environ["SQLITE_PATH"]
JWT_SECRET = os.environ["JWT_SECRET"].encode()
MAX_ID = 2**63 - 1  # SQLite's INTEGER range; larger ids cannot exist
WHITESPACE = "\t\n\v\f\r                  　﻿"
