from fastapi import APIRouter, Depends, UploadFile, File
from app.services.auth_service import get_current_user
from app.services.photo_service import upload_photo
from app.models.user import User

router = APIRouter(prefix="/photos", tags=["photos"])


@router.post("/upload")
async def upload_photo_endpoint(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    photo_url = await upload_photo(file)
    return {"photo_url": photo_url}
