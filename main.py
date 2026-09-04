from fastapi import FastAPI, Depends, HTTPException
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi.security import OAuth2PasswordRequestForm
from database import get_db
from jose import jwt
import models
import schemas
import auth

app = FastAPI(
    swagger_ui_parameters={
        "persistAuthorization": True
    }
)



@app.get('/contacts')
def get_contacts(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user)
):
    contacts = db.query(models.Contact).filter(
        models.Contact.user_id == current_user.id
    ).all()

    return contacts

@app.get('/contacts/search')
def contact_search(
        query: str,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user)
):
    contacts = db.query(models.Contact).filter(
        models.Contact.user_id == current_user.id,
        or_(
            models.Contact.name.ilike(f'%{query}%'),
            models.Contact.last_name.ilike(f'%{query}%'),
            models.Contact.email.ilike(f'%{query}%')
        )
    ).all()

    return contacts

@app.get('/contacts/birthdays/')
def upcoming_birthdays(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user)
):
    today = date.today()
    next_week = today + timedelta(days=7)

    contacts = db.query(models.Contact).filter(
        models.Contact.user_id == current_user.id
    ).all()

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
def get_contacts(
        contact_id: int, db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user)
):
    contact = db.query(models.Contact).filter(
        models.Contact.id == contact_id,
        models.Contact.user_id == current_user.id
    ).first()

    if contact is None:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )

    return contact

@app.post('/contacts', status_code=201)
def create_contact(
    contact: schemas.Contact,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    new_contact = models.Contact(
        user_id=current_user.id,
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
def update_contact(
        contact_id: int,
        contact: schemas.Contact,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user)
):
    db_contact = db.query(models.Contact).filter(
        models.Contact.id == contact_id,
        models.Contact.user_id == current_user.id
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
def contact_delete(
        contact_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user)):
    db_contact = db.query(models.Contact).filter(
        models.Contact.id == contact_id,
        models.Contact.user_id == current_user.id
    ).first()

    if db_contact is None:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )
    db.delete(db_contact)
    db.commit()

    return {"message": "Contact deleted"}

@app.post(
    '/register',
    status_code=201,
    response_model=schemas.UserResponse)
def register_user(user:schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="User with this email already exists"
        )

    hashed_password = auth.hash_password(user.password)

    new_user = models.User(
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.post('/login')
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(
        models.User.email == form_data.username
    ).first()

    if not db_user or not auth.verify_password(
        form_data.password,
        db_user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = auth.create_access_token(
        {"sub": str(db_user.id)}
    )

    refresh_token = auth.create_refresh_token(
        {"sub": str(db_user.id)}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.post('/refresh')
def refresh_access_token(
    token_data: schemas.RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    refresh_token = token_data.refresh_token

    try:
        payload = jwt.decode(
            refresh_token,
            auth.SECRET_KEY,
            algorithms=[auth.ALGORITHM]
        )
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=401,
            detail="Invalid token type"
        )

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    db_user = db.query(models.User).filter(
        models.User.id == int(user_id)
    ).first()

    if db_user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    new_access_token = auth.create_access_token(
        {"sub": str(db_user.id)}
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

