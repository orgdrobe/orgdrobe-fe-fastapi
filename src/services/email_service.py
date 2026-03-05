from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from fastapi_mail.schemas import NameEmail

from services.interfaces import EmailServiceInterface

class EmailService(EmailServiceInterface):
    def __init__(self, connection_config: ConnectionConfig):
        self._fm = FastMail(connection_config)

    async def send_verification_email(self, user_email: str, code: str) -> None:
        message = MessageSchema(
            subject="Ваш код підтвердження",
            recipients=[NameEmail(name="", email=user_email)],
            body=self._get_verification_template(code),
            subtype=MessageType.html
        )
        await self._fm.send_message(message)

    def _get_verification_template(self, code: int) -> str:
        return f"""
        <html>
            <body style="margin: 0; padding: 0; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f4f4f7; color: #51545e;">
                <table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="background-color: #f4f4f7; padding: 20px;">
                    <tr>
                        <td align="center">
                            <table width="100%" style="max-width: 570px; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); overflow: hidden;" cellpadding="0" cellspacing="0" role="presentation">
                                <tr>
                                    <td style="padding: 25px; text-align: center; background-color: #4CAF50;">
                                        <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: bold;">Авторизація</h1>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 35px; text-align: center;">
                                        <p style="font-size: 16px; line-height: 1.5; color: #51545e;">Вітаємо! Ви отримали цей лист для підтвердження реєстрації.</p>
                                        <p style="font-size: 16px; line-height: 1.5; color: #51545e; margin-bottom: 25px;">Ваш код:</p>
                                        
                                        <div style="background-color: #f4f4f7; border-radius: 4px; padding: 20px; margin: 0 auto; display: inline-block; letter-spacing: 5px;">
                                            <span style="font-size: 32px; font-weight: bold; color: #333333; font-family: monospace;">{code}</span>
                                        </div>
                                        
                                        <p style="font-size: 14px; line-height: 1.5; color: #9da3ae; margin-top: 25px;">
                                            Цей код дійсний протягом 15 хвилин.<br>
                                            Якщо ви не запитували цей код, просто видаліть цей лист.
                                        </p>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 15px; text-align: center; background-color: #f9fafb;">
                                        <p style="font-size: 12px; color: #b0adc5; margin: 0;">Автоматичне повідомлення • {self.__class__.__name__}</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
        </html>
        """