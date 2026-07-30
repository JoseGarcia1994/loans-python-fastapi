# 🌐 Third-party
from fastapi_mail import FastMail, MessageSchema, MessageType

# 📁 Local imports
from ..core.email import mail_conf

async def send_welcome_email(email: str, first_name: str):
    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0; padding:0; background-color:#f4f5f7; font-family: Arial, Helvetica, sans-serif;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f5f7; padding:40px 0;">
            <tr>
                <td align="center">
                    <table role="presentation" width="480" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:8px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.08);">

                        <!-- Header -->
                        <tr>
                            <td style="background-color:#1e3a5f; padding:32px 40px; text-align:center;">
                                <h1 style="margin:0; color:#ffffff; font-size:22px; font-weight:600;">
                                    Sistema de Préstamos
                                </h1>
                            </td>
                        </tr>

                        <!-- Body -->
                        <tr>
                            <td style="padding:40px;">
                                <h2 style="margin:0 0 16px 0; color:#1e3a5f; font-size:20px;">
                                    ¡Bienvenido, {first_name}! 👋
                                </h2>
                                <p style="margin:0 0 16px 0; color:#4a4a4a; font-size:15px; line-height:1.6;">
                                    Tu cuenta ha sido creada exitosamente. Ya puedes iniciar sesión
                                    y comenzar a gestionar tus clientes, préstamos y pagos desde
                                    un solo lugar.
                                </p>

                                <table role="presentation" cellpadding="0" cellspacing="0" style="width:100%; margin:24px 0;">
                                    <tr>
                                        <td style="background-color:#f0f4f8; border-radius:6px; padding:16px;">
                                            <p style="margin:0; color:#1e3a5f; font-size:14px; font-weight:600;">
                                                📧 Correo registrado
                                            </p>
                                            <p style="margin:4px 0 0 0; color:#4a4a4a; font-size:14px;">
                                                {email}
                                            </p>
                                        </td>
                                    </tr>
                                </table>

                                <p style="margin:24px 0 0 0; color:#8a8a8a; font-size:13px; line-height:1.6;">
                                    Si tú no creaste esta cuenta, puedes ignorar este mensaje de forma segura.
                                </p>
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td style="background-color:#f9fafb; padding:20px 40px; text-align:center; border-top:1px solid #eaeaea;">
                                <p style="margin:0; color:#a0a0a0; font-size:12px;">
                                    © {2026} Sistema de Préstamos · Este es un correo automático
                                </p>
                            </td>
                        </tr>

                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    message = MessageSchema(
        subject="Bienvenido al Sistema de Préstamos",
        recipients=[email],
        body=html,
        subtype=MessageType.html,
    )

    fm = FastMail(mail_conf)
    await fm.send_message(message)