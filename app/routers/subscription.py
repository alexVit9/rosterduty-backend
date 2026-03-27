from fastapi import APIRouter, Depends
from fastapi_mail import FastMail, MessageSchema, MessageType
from app.core.email import mail_config
from app.services.auth_service import get_current_user
from app.schemas.completed_checklist import SubscriptionRequestBody
from app.models.user import User

router = APIRouter(prefix="/subscription", tags=["subscription"])

ADMIN_EMAIL = "alexvitorskaya@gmail.com"

PLAN_NAMES = {
    "professional": "Профессиональный (€9/мес)",
    "corporate": "Корпоративный (€49/мес)",
}

BILLING_NAMES = {
    "monthly": "Ежемесячно",
    "yearly": "Ежегодно (-20%)",
}


@router.post("/request")
async def request_subscription(
    data: SubscriptionRequestBody,
    current_user: User = Depends(get_current_user),
):
    plan_label = PLAN_NAMES.get(data.plan, data.plan)
    billing_label = BILLING_NAMES.get(data.billing, data.billing)

    body = f"""Новая заявка на подписку RosterDuty

Пользователь: {current_user.name}
Email: {current_user.email}
Ресторан ID: {current_user.restaurant_id}

Выбранный план: {plan_label}
Тип оплаты: {billing_label}
"""

    message = MessageSchema(
        subject="Новая заявка на подписку — RosterDuty",
        recipients=[ADMIN_EMAIL],
        body=body,
        subtype=MessageType.plain,
    )

    fm = FastMail(mail_config)
    await fm.send_message(message)

    return {"detail": "Ваша заявка отправлена. Мы свяжемся с вами в ближайшее время."}
