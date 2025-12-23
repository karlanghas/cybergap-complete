"""
Servicio de Envío de Emails
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
from datetime import datetime
import logging

from ..models import SMTPConfig, Company
from .security import decrypt_password

logger = logging.getLogger(__name__)

# Configuración SMTP por defecto del sistema
DEFAULT_SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
DEFAULT_SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
DEFAULT_SMTP_USER = os.getenv("SMTP_USER", "")
DEFAULT_SMTP_PASS = os.getenv("SMTP_PASS", "")
DEFAULT_SMTP_FROM = os.getenv("SMTP_FROM", "noreply@cybergap.local")
DEFAULT_SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "CyberGAP")

BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")


class EmailService:
    """Servicio para envío de correos electrónicos"""
    
    def __init__(self, smtp_config: Optional[SMTPConfig] = None):
        """
        Inicializar servicio de email
        
        Args:
            smtp_config: Configuración SMTP de empresa (opcional, usa default si no se provee)
        """
        if smtp_config and smtp_config.is_active:
            self.host = smtp_config.host
            self.port = smtp_config.port
            self.username = smtp_config.username
            self.password = decrypt_password(smtp_config.password)
            self.use_tls = smtp_config.use_tls
            self.use_ssl = smtp_config.use_ssl
            self.from_email = smtp_config.from_email
            self.from_name = smtp_config.from_name or "CyberGAP"
            self.reply_to = smtp_config.reply_to
        else:
            self.host = DEFAULT_SMTP_HOST
            self.port = DEFAULT_SMTP_PORT
            self.username = DEFAULT_SMTP_USER
            self.password = DEFAULT_SMTP_PASS
            self.use_tls = True
            self.use_ssl = False
            self.from_email = DEFAULT_SMTP_FROM
            self.from_name = DEFAULT_SMTP_FROM_NAME
            self.reply_to = None
    
    def _get_connection(self):
        """Obtener conexión SMTP"""
        if self.use_ssl:
            server = smtplib.SMTP_SSL(self.host, self.port)
        else:
            server = smtplib.SMTP(self.host, self.port)
            if self.use_tls:
                server.starttls()
        
        if self.username and self.password:
            server.login(self.username, self.password)
        
        return server
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Enviar correo electrónico
        
        Returns:
            bool: True si se envió correctamente
        """
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email
            
            if self.reply_to:
                msg["Reply-To"] = self.reply_to
            
            # Versión texto plano
            if text_content:
                part1 = MIMEText(text_content, "plain")
                msg.attach(part1)
            
            # Versión HTML
            part2 = MIMEText(html_content, "html")
            msg.attach(part2)
            
            # Enviar
            with self._get_connection() as server:
                server.sendmail(self.from_email, to_email, msg.as_string())
            
            logger.info(f"Email enviado a {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email a {to_email}: {str(e)}")
            return False
    
    def test_connection(self) -> tuple[bool, str]:
        """
        Probar conexión SMTP
        
        Returns:
            tuple: (success, message)
        """
        try:
            with self._get_connection() as server:
                server.noop()
            return True, "Conexión exitosa"
        except Exception as e:
            return False, str(e)


def get_questionnaire_email_template(
    user_name: str,
    company_name: str,
    questionnaire_name: str,
    token: str,
    deadline: Optional[datetime] = None
) -> tuple[str, str]:
    """
    Generar template de email para cuestionario
    
    Returns:
        tuple: (html_content, text_content)
    """
    link = f"{BASE_URL}/survey/{token}"
    deadline_text = deadline.strftime("%d/%m/%Y %H:%M") if deadline else "Sin fecha límite"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #1e3a5f 0%, #0f766e 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .header h1 {{ margin: 0; font-size: 24px; }}
            .content {{ background: #f8fafc; padding: 30px; border: 1px solid #e2e8f0; }}
            .button {{ display: inline-block; background: #0f766e; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 20px 0; }}
            .button:hover {{ background: #0d9488; }}
            .info-box {{ background: white; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #0f766e; }}
            .footer {{ text-align: center; padding: 20px; color: #64748b; font-size: 12px; }}
            .warning {{ color: #b45309; background: #fef3c7; padding: 10px; border-radius: 5px; margin-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛡️ CyberGAP</h1>
                <p>Auditoría de Cumplimiento Normativo</p>
            </div>
            <div class="content">
                <p>Estimado/a <strong>{user_name}</strong>,</p>
                
                <p>Ha sido seleccionado/a para participar en una evaluación de cumplimiento normativo 
                de <strong>{company_name}</strong>.</p>
                
                <div class="info-box">
                    <strong>📋 Cuestionario:</strong> {questionnaire_name}<br>
                    <strong>📅 Fecha límite:</strong> {deadline_text}
                </div>
                
                <p>Por favor, haga clic en el siguiente botón para acceder al cuestionario:</p>
                
                <center>
                    <a href="{link}" class="button">Completar Cuestionario</a>
                </center>
                
                <div class="warning">
                    ⚠️ <strong>Importante:</strong> Este enlace es personal e intransferible. 
                    Solo podrá ser utilizado una vez.
                </div>
                
                <p>Si tiene alguna duda, contacte al administrador de la evaluación.</p>
            </div>
            <div class="footer">
                <p>Este es un correo automático generado por CyberGAP.<br>
                Por favor, no responda a este mensaje.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    CyberGAP - Auditoría de Cumplimiento Normativo
    
    Estimado/a {user_name},
    
    Ha sido seleccionado/a para participar en una evaluación de cumplimiento normativo de {company_name}.
    
    Cuestionario: {questionnaire_name}
    Fecha límite: {deadline_text}
    
    Para completar el cuestionario, acceda al siguiente enlace:
    {link}
    
    IMPORTANTE: Este enlace es personal e intransferible. Solo podrá ser utilizado una vez.
    
    Si tiene alguna duda, contacte al administrador de la evaluación.
    
    ---
    Este es un correo automático generado por CyberGAP.
    """
    
    return html_content, text_content


def get_reminder_email_template(
    user_name: str,
    company_name: str,
    questionnaire_name: str,
    token: str,
    deadline: Optional[datetime] = None
) -> tuple[str, str]:
    """Generar template de recordatorio"""
    link = f"{BASE_URL}/survey/{token}"
    deadline_text = deadline.strftime("%d/%m/%Y %H:%M") if deadline else "Sin fecha límite"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #b45309 0%, #d97706 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f8fafc; padding: 30px; border: 1px solid #e2e8f0; }}
            .button {{ display: inline-block; background: #d97706; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; }}
            .footer {{ text-align: center; padding: 20px; color: #64748b; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>⏰ Recordatorio</h1>
                <p>Cuestionario pendiente de completar</p>
            </div>
            <div class="content">
                <p>Estimado/a <strong>{user_name}</strong>,</p>
                
                <p>Le recordamos que tiene pendiente completar el cuestionario 
                "<strong>{questionnaire_name}</strong>" de {company_name}.</p>
                
                <p><strong>Fecha límite:</strong> {deadline_text}</p>
                
                <center>
                    <a href="{link}" class="button">Completar Ahora</a>
                </center>
            </div>
            <div class="footer">
                <p>CyberGAP - Auditoría de Cumplimiento Normativo</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    RECORDATORIO - Cuestionario Pendiente
    
    Estimado/a {user_name},
    
    Le recordamos que tiene pendiente completar el cuestionario "{questionnaire_name}" de {company_name}.
    
    Fecha límite: {deadline_text}
    
    Acceda al siguiente enlace para completar:
    {link}
    
    CyberGAP - Auditoría de Cumplimiento Normativo
    """
    
    return html_content, text_content
