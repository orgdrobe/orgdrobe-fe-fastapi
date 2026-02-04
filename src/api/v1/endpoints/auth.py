from fastapi import APIRouter

from schemas.user import UserRegister, UserOut

router = APIRouter()


@router.post("/register", response_model=UserOut)
async def register(payload: UserRegister) -> UserOut:

    return UserOut()

# Додай контекст наприклад 
#class TransactionContext()
#   def rollback()
#   def commit()

# @router.post("/login", response_model=TempData)
# async def login(db: TempData, credentials: TempData):
#     return None

# @router.post("/google", response_model=TempData)
# async def google(db: TempData, credentials: TempData):
#     return None