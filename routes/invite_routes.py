from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database.database import get_db

from models.invite_model import ConfirmInviteSchema, IncomingInfoSchema, InviteSchema
from controllers.invite_controller import create_invite, confirm_invite
invite_routes = APIRouter()
@invite_routes.post("/invites")
async def createInvite(incoming_info: IncomingInfoSchema, db: Session = Depends(get_db)):
    new_invite = await create_invite(incoming_info, db)
    return new_invite

@invite_routes.post("/confirm")
async def confirmInvite(data: ConfirmInviteSchema, db: Session = Depends(get_db)):
    confirmed_invite = confirm_invite(data.token, data.password, db)
    if not confirmed_invite:
        raise HTTPException(status_code=404, detail="Invite not found or already confirmed")
    return confirmed_invite
