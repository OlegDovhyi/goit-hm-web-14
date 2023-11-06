from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status, Path
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Contact, User
from src.sсhemas import ContactCreate, ContactResponse
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service
from src.sсhemas import ContactResponse

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get(
    "/all",
    response_model=List[ContactResponse],
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_contacts(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> List[Contact]:
    """
    The get_contacts function returns a list of contacts for the current user.

    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user from the database
    :param : Get the current user
    :return: A list of contact objects
    """
    contacts = await repository_contacts.get_contacts(current_user, db)
    return contacts


@router.get(
    "/birthday",
    response_model=List[ContactResponse],
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def contacts_birthday(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> List[Contact]:
    """
    The contacts_birthday function returns a list of contacts with birthdays in the next week.

    :param db: Session: Get a database session
    :param current_user: User: Get the user id from the jwt token
    :param : Pass the database session to the function
    :return: A list of contacts with birthday in the next 7 days
    """
    contacts = await repository_contacts.get_birthday_per_week(current_user, db)
    if contacts is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contacts not found"
        )
    return contacts


@router.get(
    "/{contact_id}",
    response_model=ContactResponse,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_contact(
    contact_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Contact:
    """
    The get_contact function returns a contact by its id.

    :param contact_id: int: Get the contact id from the url
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user from the database
    :param : Get the contact id from the url
    :return: A contact object
    """
    contact = await repository_contacts.get_contact_by_id(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found!")
    return contact


@router.get(
    "/search/{query}",
    response_model=List[ContactResponse],
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def search_contact(
    query: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Contact:
    """
    The search_contact function searches for a contact by name.

    :param query: str: Get the query string from the url
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user from the database
    :param : Get the current user from the database
    :return: A contact object
    """
    contact = await repository_contacts.search_contact(query, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found!")
    return contact


@router.post(
    "/",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def create_contact(
    body: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Contact:
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactCreate: Validate the request body
    :param db: Session: Get the database session
    :param current_user: User: Get the user who is currently logged in
    :param : Get the current user from the database
    :return: A contact object
    """
    contact = await repository_contacts.get_contact_by_email(
        body.email, current_user, db
    )
    if contact:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email is exists!"
        )
    contact = await repository_contacts.create_contact(body, current_user, db)
    return contact


@router.put(
    "/{contact_id}",
    response_model=ContactResponse,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def update_contacts(
    body: ContactCreate,
    contact_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Contact:
    """
    The update_contacts function updates a contact in the database.

    :param body: ContactCreate: Pass the data that we want to update in our database
    :param contact_id: int: Get the contact id from the url
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user from the database
    :param : Get the contact id
    :return: A contact object
    """
    contact = await repository_contacts.update_contact(
        contact_id, body, current_user, db
    )
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found!")
    return contact


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def delete_contacts(
    contact_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> None:
    """
    The delete_contacts function deletes a contact from the database.

    :param contact_id: int: Get the contact id from the url
    :param db: Session: Get the database session
    :param current_user: User: Check if the user is authenticated or not
    :param : Get the contact id from the url
    :return: None
    """
    contact = await repository_contacts.delete_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found!")
