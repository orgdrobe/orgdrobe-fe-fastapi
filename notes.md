architecture of FastAPI (kinda, i think):

- scemas(basemodels) -> swagger
- models -> database

---

Copy Paste commands 

win

```
python -m venv .venv-win
.venv-win\Scripts\activate
pip install -r requirements_manual.txt
pip freeze > requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

```

```
.venv-win\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

```

deb

```
python3 -m venv .venv-debian
source .venv-debian/bin/activate
pip install -r requirements_manual.txt
pip freeze > requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

```

```
source .venv-debian/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

```
