from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver, Signal
from django_rest_passwordreset.signals import reset_password_token_created

from mtv.models import ConfirmEmailToken, User


new_user_registered = Signal()

new_order = Signal()

@receiver(new_user_registered)
def new_user_registered_signal(user_id, **kwargs):
    """
    отправляем письмо с подтрердждением почты
    """
    # send an e-mail to the user
    token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user_id)

    mailbox = f'Ваш токен для подтверждения: {token.key}\nДля завершения перейдите по ссылке: http://127.0.0.1:8000/user/confirm'
    
    msg = EmailMultiAlternatives(
        # title:
        f"Password Reset Token for {token.user.email}",
        # message:
        mailbox,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [token.user.email]
    )
    msg.send()

@receiver(new_order)
def new_order_signal(user_id, **kwargs):
    """
    отправяем письмо при изменении статуса заказа
    """
    # send an e-mail to the user
    user = User.objects.get(id=user_id)

    msg = EmailMultiAlternatives(
        # title:
        f"Обновление статуса заказа",
        # message:
        'Ваш заказ сформирован.',
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [user.email]
    )
    msg.send()