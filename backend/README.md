## About
This is my attempt to create a lightweight backend that can achive a maximum number of users within respective constraints.

I'll use `Starlatte` as my main framework. In theory this should be enough to handle the scope of this project.
If smth will be needed, I'll try to integrate the solution by myself. 
As a result I'll get deeper understanding how many high-level abstraction objects work(`Pydantic`, `pyjwt`, etc)

## Backend Setup
To create a python env run this command in `backend` dir:
```bash
python -m venv venv
```
To activate an env run:
```bash
source vevn/bin/activate
```
Install all deps:
```bash
pip install -r requirements.txt
```
Run server:
```bash
uvicorn main:app
```
Test authentication:
```bash
curl -X POST http://127.0.0.1:8000/posts \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NSIsInVzZXJuYW1lIjoiRGltY2hlY2siLCJpYXQiOjE3OTI5NTY0MDksImV4cCI6MTc5Mjk2MDAwOX0.Pww32JDCOmeRRkyE98VhoA6rTkXLOHBg-yNhiCmt7Rk" \
     -H "Content-Type: application/json" \
     -d '{"hello": "world"}'
```