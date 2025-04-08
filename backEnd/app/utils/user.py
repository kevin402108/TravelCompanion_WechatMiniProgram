from fastapi import Depends
from sqlalchemy.orm import Session
from backEnd.app.database import get_database
from backEnd.app.models import User

def checkUserExist(
    id:int,
    db:Session = Depends(get_database)
) -> tuple:
    user = db.query(User).filter(User.id == id).first()
    if not user:
        return (False,None)
    return (True,user)
        