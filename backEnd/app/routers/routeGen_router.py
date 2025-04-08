from fastapi.responses import JSONResponse
from pydantic import BaseModel
from backEnd.app.models import Route
from  backEnd.app.utils.logger import setup_logger
import backEnd.app.utils.exceptions as exceptions
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, ProgrammingError, DataError, IntegrityError
from fastapi import APIRouter, Depends
from backEnd.app.database import get_database
from backEnd.app.utils.user import checkUserExist

routeGen_router = APIRouter()

logger = setup_logger('route_generate_router')

class RouteGenModel(BaseModel):
    id:int
    destination:str
    travelDays:int
    budget:int
    preferences:str
    
@routeGen_router.post('/route_auto_generate')
async def routeAutoGenerate(
    RouteRequire:RouteGenModel,
    db:Session = Depends(get_database)
):
    queryResult = checkUserExist(RouteRequire.id)
    if not queryResult[0]:
        raise exceptions.UserNotFoundError()
    
    new_Route = Route(
        user_id=RouteRequire.id,
        destination = RouteRequire.destination,
        travel_days = RouteRequire.travelDays,
        budget = RouteRequire.budget,
        preference = RouteRequire.preferences
    )
    
    db.add(new_Route)
    db.flush()
    db.commit()
    
    
    
    
    
    