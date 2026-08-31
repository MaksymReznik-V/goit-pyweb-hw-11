from fastapi import FastAPI, Depends, HTTPException
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import SessionLocal
import models
import schemas

app = FastAPI()



def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.get('/contacts')
def get_contacts(db: Session = Depends(get_db)):
    contact = db.query(models.Contact).all()
    return contact

@app.get('/contacts/search')
def contact_search(query: str, db: Session = Depends(get_db)):
    contacts = db.query(models.Contact).filter(
        or_(
        models.Contact.name.ilike(f'%{query}%'),
        models.Contact.last_name.ilike(f'%{query}%'),
        models.Contact.email.ilike(f'%{query}%')
        )
    ).all()

    return contacts

@app.get('/contacts/birthdays/')
def upcoming_birthdays(db: Session = Depends(get_db)):
    today = date.today()
    next_week = today + timedelta(days=7)

    contacts = db.query(models.Contact).all()

    upcoming = []

    for contact in contacts:
        birthday_this_year = contact.birthday.replace(year=today.year)

        if birthday_this_year < today:
            birthday_this_year = birthday_this_year.replace(
                year=today.year + 1
            )

        if today <= birthday_this_year <= next_week:
            upcoming.append(contact)

    return upcoming

@app.get('/contacts/{contact_id}')
def get_contacts(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(models.Contact).filter(
        models.Contact.id == contact_id
    ).first()

    if contact is None:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )

    return contact

@app.post('/contacts')
def create_contact(contact: schemas.Contact, db: Session = Depends(get_db)):
    new_contact = models.Contact(
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

@app.put('/contacts/{contact_id}')
def update_contact(contact_id: int, contact: schemas.Contact, db: Session = Depends(get_db)):
    db_contact = db.query(models.Contact).filter(
        models.Contact.id == contact_id
    ).first()

    if db_contact is None:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )

    db_contact.name = contact.name
    db_contact.last_name = contact.last_name
    db_contact.email = contact.email
    db_contact.phone = contact.phone
    db_contact.birthday = contact.birthday
    db_contact.additional_info = contact.additional_info

    db.commit()
    db.refresh(db_contact)

    return db_contact

@app.delete('/contacts/{contact_id}')
def contact_delete(contact_id: int, db: Session = Depends(get_db)):
    db_contact = db.query(models.Contact).filter(
        models.Contact.id == contact_id
    ).first()

    if db_contact is None:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )
    db.delete(db_contact)
    db.commit()

    return {"message": "Contact deleted"}



