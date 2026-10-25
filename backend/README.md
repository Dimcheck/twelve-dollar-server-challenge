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
Run server from `backend` dir:
```bash
uvicorn main:app
```
Run tests from `backend` dir:
```bash
pytest
```
