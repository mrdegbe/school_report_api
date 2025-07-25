# ✅ << your login, register, token endpoints

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import security  # your auth utils
from app.crud import user as crud_user
from app.models import user as models_user
from app.schemas import token as schemas_token  # optional, if you have a Token schema
from app.core import dependencies

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=schemas_token.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(dependencies.get_db),
):
    user = crud_user.get_user_by_email(db, form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    if not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": str(user.role.value),
        "name": user.name,
    }

    access_token = security.create_access_token(data=token_data)
    return {"access_token": access_token, "token_type": "bearer"}
