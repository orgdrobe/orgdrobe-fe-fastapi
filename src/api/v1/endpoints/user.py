from fastapi import APIRouter


router = APIRouter()

@router.get("/test")
def test_route() -> dict[str,str]:
    return {"message": "Hello world!"}
