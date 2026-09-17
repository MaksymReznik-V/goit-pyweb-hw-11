import unittest
from unittest.mock import MagicMock
from datetime import date

from sqlalchemy.orm import Session

from models import Contact, User
from schemas import Contact as ContactSchema
from repository.contacts import (
    get_contacts,
    get_contact,
    search_contacts,
    create_contact,
    update_contact,
    delete_contact,
)


class TestContacts(unittest.TestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().all.return_value = contacts

        result = get_contacts(
            db=self.session,
            user_id=self.user.id
        )

        self.assertEqual(result, contacts)

    def test_get_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact

        result = get_contact(
            contact_id=1,
            db=self.session,
            user_id=self.user.id
        )

        self.assertEqual(result, contact)

    def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None

        result = get_contact(
            contact_id=1,
            db=self.session,
            user_id=self.user.id
        )

        self.assertIsNone(result)

    def test_search_contacts(self):
        contacts = [Contact(), Contact()]
        self.session.query().filter().all.return_value = contacts

        result = search_contacts(
            query="Max",
            db=self.session,
            user_id=self.user.id
        )

        self.assertEqual(result, contacts)

    def test_create_contact(self):
        body = ContactSchema(
            name="Max",
            last_name="Test",
            email="max@example.com",
            phone="123456789",
            birthday=date(2000, 1, 1),
            additional_info="Test contact"
        )

        result = create_contact(
            contact=body,
            db=self.session,
            user_id=self.user.id
        )

        self.assertEqual(result.name, body.name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.user_id, self.user.id)

    def test_update_contact_found(self):
        contact = Contact(
            id=1,
            user_id=self.user.id,
            name="Old",
            last_name="Name",
            email="old@example.com"
        )

        self.session.query().filter().first.return_value = contact

        body = ContactSchema(
            name="New",
            last_name="Name",
            email="new@example.com",
            phone="987654321",
            birthday=date(1995, 5, 5),
            additional_info="Updated"
        )

        result = update_contact(
            contact_id=1,
            contact=body,
            db=self.session,
            user_id=self.user.id
        )

        self.assertEqual(result, contact)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.email, body.email)

    def test_update_contact_not_found(self):
        self.session.query().filter().first.return_value = None

        body = ContactSchema(
            name="New",
            last_name="Name",
            email="new@example.com",
            phone="987654321",
            birthday=date(1995, 5, 5),
            additional_info="Updated"
        )

        result = update_contact(
            contact_id=1,
            contact=body,
            db=self.session,
            user_id=self.user.id
        )

        self.assertIsNone(result)

    def test_delete_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact

        result = delete_contact(
            contact_id=1,
            db=self.session,
            user_id=self.user.id
        )

        self.assertEqual(result, contact)

    def test_delete_contact_not_found(self):
        self.session.query().filter().first.return_value = None

        result = delete_contact(
            contact_id=1,
            db=self.session,
            user_id=self.user.id
        )

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()