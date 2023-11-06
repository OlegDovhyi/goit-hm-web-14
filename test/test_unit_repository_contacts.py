from datetime import datetime
import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.sсhemas import ContactCreate
from src.repository.contacts import (
    get_contacts,
    get_contact_by_id,
    search_contact,
    create_contact,
    update_contact,
    delete_contact,
    get_birthday_per_week,
)


class TestContacts(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contact(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().all.return_value = contacts
        result = await get_contacts(user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact_by_id(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact_by_id(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        self.body = ContactCreate(
            firstname="John",
            lastname="Dou",
            email="test@test.com",
            phone="1234567890",
            birthday=datetime.now().date(),
        )
        result = await create_contact(body=self.body, user=self.user, db=self.session)
        self.assertEqual(result.firstname, self.body.firstname)
        self.assertEqual(result.lastname, self.body.lastname)
        self.assertEqual(result.email, self.body.email)
        self.assertEqual(result.phone, self.body.phone)
        self.assertEqual(result.birthday, self.body.birthday)
        self.assertTrue(hasattr(result, "id"))

    async def test_delete_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await delete_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_delete_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await delete_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_contact_found(self):
        body = ContactCreate(
            firstname="John",
            lastname="Dou",
            email="test@test.com",
            phone="1234567890",
            birthday=datetime.now().date(),
        )
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        self.session.commit.return_value = None
        result = await update_contact(
            contact_id=1, body=body, user=self.user, db=self.session
        )
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        body = ContactCreate(
            firstname="John",
            lastname="Dou",
            email="test@test.com",
            phone="1234567890",
            birthday=datetime.now().date(),
        )
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_contact(
            contact_id=1, body=body, user=self.user, db=self.session
        )
        self.assertIsNone(result)

    async def test_search_contact_found(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().all.return_value = contacts
        result = await search_contact(
            query="test@test.com", user=self.user, db=self.session
        )
        self.assertEqual(result, contacts)

    async def test_search_contact_not_found(self):
        self.session.query().filter().all.return_value = None
        result = await search_contact(
            query="tset@test.com", user=self.user, db=self.session
        )
        self.assertIsNone(result)

    async def test_get_birthday_per_week(self):
        contacts = [
            Contact(birthday=datetime.now().date()),
            Contact(birthday=datetime.now().date()),
            Contact(birthday=datetime.now().date()),
        ]
        self.session.query().filter().all.return_value = contacts
        result = await get_birthday_per_week(user=self.user, db=self.session)
        self.assertEqual(result, contacts)


if __name__ == "__main__":
    unittest.main()
