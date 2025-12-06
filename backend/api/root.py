from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def root():
    return {"message": "Bible App Backend API is running"}
