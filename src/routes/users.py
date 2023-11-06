import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings
from src.sсhemas import UserDb

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserDb)
async def read_users_me(
    current_user: User = Depends(auth_service.get_current_user),
) -> User:
    """
    The read_users_me function returns the current user's information.

    :param current_user: User: Get the current user
    :return: The current user object
    """
    return current_user


@router.patch("/avatar", response_model=UserDb)
async def update_avatar_user(
    avatar: UploadFile = File(),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """
    The update_avatar_user function updates the avatar of a user.

    :param avatar: UploadFile: Upload the file to cloudinary
    :param current_user: User: Get the current user's email and username
    :param db: Session: Pass the database session to the repository layer
    :param : Get the current user from the database
    :return: A user object
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )

    r = cloudinary.uploader.upload(
        avatar.file, public_id=f"ContactsApp/{current_user.username}", overwrite=True
    )
    src_url = cloudinary.CloudinaryImage(
        f"ContactsApp/{current_user.username}"
    ).build_url(width=250, height=250, crop="fill", version=r.get("version"))
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user
