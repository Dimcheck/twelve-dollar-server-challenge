import sqlite3

from consts import SQLITE_PATH

db = sqlite3.connect(SQLITE_PATH, isolation_level=None, check_same_thread=False, cached_statements=32)
db.execute("PRAGMA journal_mode = WAL")
db.execute("PRAGMA synchronous = NORMAL")  # rule 6: WAL + NORMAL
db.execute("PRAGMA busy_timeout = 5000")
db.execute("PRAGMA mmap_size = 1073741824")  # read the file through the OS page cache, no copies
db.execute("PRAGMA cache_size = -65536")  # 64 MiB
db.execute("PRAGMA temp_store = MEMORY")


BASE_SELECT = """
SELECT p.id, p.body, p.created_at, u.username, (SELECT count(*) FROM likes l WHERE l.post_id = p.id) as like_count
  FROM posts p JOIN users u ON u.id = p.user_id
"""
GET_BY_ID = BASE_SELECT + """WHERE p.id = ?"""
FEED = BASE_SELECT + " ORDER BY p.created_at DESC, p.id DESC LIMIT 20"
INSERT = "INSERT INTO posts (user_id, body) VALUES (?, ?) RETURNING id, created_at"


INSERT_LIKE = """
INSERT INTO likes (user_id, post_id)
SELECT ?1, ?2 WHERE EXISTS (SELECT 1 FROM posts WHERE id = ?2)
ON CONFLICT (user_id, post_id) DO NOTHING
"""
POST_EXISTS = "SELECT 1 FROM posts WHERE id = ?"