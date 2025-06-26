# SocialWardrobe

Created by maksymstepaniuk ([maxstepanyuk](https://github.com/maxstepanyuk) on github). The original repository:  [social-wardrobe-fastapi](https://github.com/maxstepanyuk/social-wardrobe-fastapi)

Before using this in your own works, please ask me first.

Contact me or see what I'm up to - [maksstep.com](https://maksstep.com) or [linktree](https://linktr.ee/purpexe)

# FastAPI

[Swagger documentation `http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs)

[Redoc documentation `http://127.0.0.1:8000/redoc`](http://127.0.0.1:8000/redoc)

[OpenAPI and JSON Schema `http://127.0.0.1:8000/openapi.json`](http://127.0.0.1:8000/openapi.json)

## Python and virtual environments on Debian 12

**Install**

On Debian/Ubuntu systems, you need to install the python3-venv package using the following command.

```bash
sudo apt install python3-venv
```
After installing the python3-venv package, recreate your virtual environment.

**Create**

```bash
python3 -m venv .venv
```

`.venv` - name on the virtual environment

**How to activate and deactivate**

activate:

```bash
source .venv/bin/activate
```

*run python code at this stage* 

deactivate (just by entering this):

```bash
deactivate
```

## Install requirements

```bash
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --port=8000 --reload
# uvicorn main:app --host 0.0.0.0 --port 8000 --reload # you can also open to a local network
```

`main:app` - in file "main.py" run "app". 

`--port=8000` - use port 8000. 

`--reload` - reload server on file update