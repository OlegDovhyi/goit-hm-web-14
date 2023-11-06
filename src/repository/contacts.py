from typing import List
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.database.models import Contact, User
from src.sсhemas import ContactCreate


async def get_contacts(user: User, db: Session) -> List[Contact]:
    """
    The get_contacts function returns a list of contacts for the user.

    :param user: User: Get the user id from the database
    :param db: Session: Pass the database session to the function
    :return: A list of contacts
    """
    contacts = db.query(Contact).filter(Contact.user_id == user.id).all()
    return contacts


async def get_contact_by_id(contact_id: int, user: User, db: Session) -> Contact:
    """
    The get_contact_by_id function returns a contact by its id.

    :param contact_id: int: Specify the id of the contact that we want to get
    :param user: User: Get the user object from the database
    :param db: Session: Connect to the database
    :return: A contact object
    """
    contacts = (
        db.query(Contact)
        .filter(and_(Contact.id == contact_id, Contact.user_id == user.id))
        .first()
    )
    return contacts


async def get_contact_by_email(email: str, user: User, db: Session) -> Contact:
    """
    The get_contact_by_email function returns a contact by email.

    :param email: str: Get the email of a contact
    :param user: User: Get the user_id from the database
    :param db: Session: Pass the database session to the function
    :return: The contact with the given email address
    """
    contacts = (
        db.query(Contact)
        .filter(and_(Contact.email == email, Contact.user_id == user.id))
        .first()
    )
    return contacts


async def search_contact(query: str, user: User, db: Session) -> List[Contact]:
    """
    The search_contact function searches for a contact in the database.

    :param query: str: Search the database for a contact
    :param user: User: Get the user id of the current user
    :param db: Session: Pass the database session to the function
    :return: A list of contact objects
    """
    contact = (
        db.query(Contact)
        .filter(and_(Contact.firstname.ilike(f"%{query}%"), Contact.user_id == user.id))
        .all()
    )
    if contact:
        return contact
    contact = (
        db.query(Contact)
        .filter(and_(Contact.lastname.ilike(f"%{query}%"), Contact.user_id == user.id))
        .all()
    )
    if contact:
        return contact
    contact = (
        db.query(Contact)
        .filter(and_(Contact.email.ilike(f"%{query}%"), Contact.user_id == user.id))
        .all()
    )
    if contact:
        return contact


async def create_contact(body: ContactCreate, user: User, db: Session) -> Contact:
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactCreate: Create a new contact
    :param user: User: Get the user_id from the user object
    :param db: Session: Access the database
    :return: A contact object
    """
    contact = Contact(**body.model_dump(), user_id=user.id)
    db.add(contact)
    db.commit()
    return contact


async def update_contact(
    contact_id: int, body: ContactCreate, user: User, db: Session
) -> Contact:
    """
    The update_contact function updates a contact in the database.

    :param contact_id: int: Specify the contact to update
    :param body: ContactCreate: Get the data from the request body
    :param user: User: Get the user's id from the database
    :param db: Session: Pass the database session to the function
    :return: A contact object
    """
    contact = await get_contact_by_id(contact_id, user, db)
    if contact:
        contact.firstname = body.firstname
        contact.lastname = body.lastname
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        db.commit()
    return contact


async def delete_contact(contact_id: int, user: User, db: Session) -> Contact:
    """
    The delete_contact function deletes a contact from the database.

    :param contact_id: int: Specify the contact id of the contact to be deleted
    :param user: User: Check if the user is authorized to delete a contact
    :param db: Session: Pass the database session to the function
    :return: The deleted contact
    """
    contact = await get_contact_by_id(contact_id, user, db)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def get_birthday_per_week(user: User, db: Session) -> List[Contact]:
    """
    The get_birthday_per_week function returns a list of contacts whose birthday is within the next 7 days.

    :param user: User: Get the user's id from the database
    :param db: Session: Connect to the database
    :return: A list of contacts that have their birthday in the next 7 days
    """
    contacts = []
    all_contacts = await get_contacts(user, db)
    for contact in all_contacts:
        if (
            timedelta(0)
            <= (
                datetime.now().date()
                - (contact.birthday.replace(year=int((datetime.now()).year)))
            )
            <= timedelta(7)
        ):
            contacts.append(contact)
    return contacts
