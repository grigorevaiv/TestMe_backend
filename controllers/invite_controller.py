from fastapi import HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime, timedelta

from models.invite_model import IncomingInfoSchema, InviteSchema, Invite
from models.user_model import User, UserSchema

async def create_invite(incoming_info: IncomingInfoSchema, db: Session):
    token = str(uuid4())
    expires_at = datetime.now() + timedelta(days=5)

    new_invite = Invite(
        email=incoming_info.email,
        first_name=incoming_info.first_name,
        last_name=incoming_info.last_name,
        token=token,
        expires_at=expires_at,
        created_by_admin_id=incoming_info.admin_id
    )

    db.add(new_invite)
    db.commit()
    db.refresh(new_invite)

    invite_link = f"{INVITE_CONFIRMATION_URL}?token={token}"
    if not invite_link:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при создании ссылки приглашения")
    
    try:
        send_invite_email(
            to_email=incoming_info.email,
            to_name=f"{incoming_info.first_name} {incoming_info.last_name}",
            invite_link=invite_link
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при отправке приглашения: {str(e)}")

    return new_invite

import os
from dotenv import load_dotenv
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from sib_api_v3_sdk.models import SendSmtpEmail

load_dotenv()

INVITE_API_KEY = os.getenv("INVITE_API_KEY")
INVITE_CONFIRMATION_URL = os.getenv("INVITE_CONFIRMATION_URL")

# настройка API-ключа
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = INVITE_API_KEY

def send_invite_email(to_email: str, to_name: str, invite_link: str):
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    send_smtp_email = SendSmtpEmail(
        to=[{"email": to_email, "name": to_name}],
        sender={"name": "TestMe", "email": "joezefin@gmail.com"},
        subject="Вы приглашены в систему",
        html_content=f"""
            <p>Привет, {to_name}!</p>
            <p>Вас пригласили в систему. Чтобы присоединиться, перейдите по ссылке:</p>
            <p><a href="{invite_link}">{invite_link}</a></p>
        """
    )

    try:
        response = api_instance.send_transac_email(send_smtp_email)
        print("Email sent. Message ID:", response.message_id)
        return response
    except ApiException as e:
        print("Ошибка при отправке email через Brevo:", e)
        raise


def confirm_invite(token: str, password: str, db: Session):
    invite = db.query(Invite).filter(Invite.token == token).first()
    if not invite:
        raise HTTPException(status_code=404, detail="Приглашение не найдено")

    if invite.confirmed:
        raise HTTPException(status_code=400, detail="Приглашение уже подтверждено")

    if invite.expires_at < datetime.now():
        raise HTTPException(status_code=400, detail="Срок действия приглашения истек")
    
    new_user = User(
        email=invite.email,
        first_name=invite.first_name,
        last_name=invite.last_name,
        assigned_to_admin_id=invite.created_by_admin_id
    )

    password_hash = hash_password(password)
    new_user.password = password_hash
    db.add(new_user)
    invite.confirmed = True
    db.commit()
    db.refresh(invite)

    return {"message": "Приглашение успешно подтверждено"}

def hash_password(password: str) -> str:
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()