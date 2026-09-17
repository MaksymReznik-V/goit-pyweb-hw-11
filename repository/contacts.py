from sqlalchemy.orm import Session
from sqlalchemy import or_

import models
import schemas


def get_contacts(db: Session, user_id: int):
    """
    Retrieve all contacts belonging to a user.

    Args:
        db: SQLAlchemy database session.
        user_id: Identifier of the contact owner.

    Returns:
        list: List of user's contacts.
    """
    return db.query(models.Contact).filter(
        models.Contact.user_id == user_id
    ).all()


def get_contact(contact_id: int, db: Session, user_id: int):
    """
    Retrieve a contact by its identifier.

    Args:
        contact_id: Contact identifier.
        db: SQLAlchemy database session.
        user_id: Identifier of the contact owner.

    Returns:
        models.Contact | None: Contact if found, otherwise None.
    """
    return db.query(models.Contact).filter(
        models.Contact.id == contact_id,
        models.Contact.user_id == user_id
    ).first()


def search_contacts(query: str, db: Session, user_id: int):
    """
    Search contacts by name, last name, or email.

    Args:
        query: Search string.
        db: SQLAlchemy database session.
        user_id: Identifier of the contact owner.

    Returns:
        list: Contacts matching the search query.
    """
    return db.query(models.Contact).filter(
        models.Contact.user_id == user_id,
        or_(
            models.Contact.name.ilike(f"%{query}%"),
            models.Contact.last_name.ilike(f"%{query}%"),
            models.Contact.email.ilike(f"%{query}%")
        )
    ).all()


def create_contact(contact: schemas.Contact, db: Session, user_id: int):
    """
    Create a new contact.

    Args:
        contact: Contact data.
        db: SQLAlchemy database session.
        user_id: Identifier of the contact owner.

    Returns:
        models.Contact: Newly created contact.
    """
    new_contact = models.Contact(
        user_id=user_id,
        name=contact.name,
        last_name=contact.last_name,
        email=contact.email,
        phone=contact.phone,
        birthday=contact.birthday,
        additional_info=contact.additional_info
    )

    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)

    return new_contact


def update_contact(
    contact_id: int,
    contact: schemas.Contact,
    db: Session,
    user_id: int
):
    """
    Update an existing contact.

    Args:
        contact_id: Contact identifier.
        contact: Updated contact data.
        db: SQLAlchemy database session.
        user_id: Identifier of the contact owner.

    Returns:
        models.Contact | None: Updated contact if found, otherwise None.
    """
    db_contact = get_contact(contact_id, db, user_id)

    if db_contact is None:
        return None

    db_contact.name = contact.name
    db_contact.last_name = contact.last_name
    db_contact.email = contact.email
    db_contact.phone = contact.phone
    db_contact.birthday = contact.birthday
    db_contact.additional_info = contact.additional_info

    db.commit()
    db.refresh(db_contact)

    return db_contact


def delete_contact(contact_id: int, db: Session, user_id: int):
    """
    Delete a contact.

    Args:
        contact_id: Contact identifier.
        db: SQLAlchemy database session.
        user_id: Identifier of the contact owner.

    Returns:
        models.Contact | None: Deleted contact if found, otherwise None.
    """
    db_contact = get_contact(contact_id, db, user_id)

    if db_contact is None:
        return None

    db.delete(db_contact)
    db.commit()

    return db_contact