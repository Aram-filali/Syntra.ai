import os
import smtplib
from typing import List, Dict, Any, Optional
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    """Service pour envoyer des emails via SMTP"""

    @staticmethod
    def _is_smtp_configured() -> bool:
        smtp_host = os.getenv("SMTP_HOST", "").strip()
        smtp_user = os.getenv("SMTP_USER", "").strip()
        smtp_password = os.getenv("SMTP_PASSWORD", "").strip()

        placeholders = {
            "your-email@gmail.com",
            "your-app-specific-password",
            "smtp.example.com",
            "...",
            "",
        }

        return (
            smtp_host not in placeholders
            and smtp_user not in placeholders
            and smtp_password not in placeholders
        )

    @staticmethod
    def _send_smtp_email(
        recipient_email: str,
        subject: str,
        html_content: str,
    ) -> bool:
        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER", "")
        smtp_password = os.getenv("SMTP_PASSWORD", "")
        from_email = os.getenv("FROM_EMAIL", "noreply@syntra.ai")
        from_name = os.getenv("FROM_NAME", "Syntra.ai")

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{from_name} <{from_email}>"
        msg["To"] = recipient_email
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
            server.ehlo()
            if smtp_port == 587:
                server.starttls()
                server.ehlo()
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.sendmail(from_email, [recipient_email], msg.as_string())

        return True
    
    @staticmethod
    def send_email(
        recipient_email: str,
        subject: str,
        html_content: str
    ) -> bool:
        """
        Envoie un email générique
        
        Args:
            recipient_email: Email du destinataire
            subject: Sujet de l'email
            html_content: Contenu HTML de l'email
        
        Returns:
            True si succès, False sinon
        """
        try:
            # En local/dev sans SMTP configure, on simule l'envoi pour ne pas bloquer les flows.
            if not EmailService._is_smtp_configured():
                print("📧 DEV MODE - Email not sent (SMTP not configured)")
                print(f"   To: {recipient_email}")
                print(f"   Subject: {subject}")
                print(f"   Content Preview: {html_content[:100]}...")
                return True

            EmailService._send_smtp_email(
                recipient_email=recipient_email,
                subject=subject,
                html_content=html_content,
            )
            print(f"Email sent successfully to {recipient_email} via SMTP")
            return True
        except Exception as e:
            print(f"Error sending verification email via SMTP: {str(e)}")
            return False
    
    @staticmethod
    def send_meeting_share_email(
        recipient_emails: List[str],
        meeting_title: str,
        sender_name: str,
        summary_text: str,
        meeting_id: int,
        actions: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Envoie un email de partage de meeting avec le résumé et les actions
        
        Args:
            recipient_emails: Liste des emails destinataires
            meeting_title: Titre du meeting
            sender_name: Nom du sender
            summary_text: Texte du résumé
            meeting_id: ID du meeting
            actions: Liste optionnelle des action items
        
        Returns:
            True si succès, False sinon
        """
        try:
            html_content = EmailService._generate_email_html(
                meeting_title=meeting_title,
                sender_name=sender_name,
                summary_text=summary_text,
                actions=actions or [],
                meeting_id=meeting_id,
            )
            subject = f"📋 {sender_name} vous partage : {meeting_title}"

            success_count = 0
            for recipient_email in recipient_emails:
                if EmailService.send_email(recipient_email, subject, html_content):
                    success_count += 1

            return success_count == len(recipient_emails)
        except Exception as e:
            print(f"Error sending meeting share email via SMTP: {str(e)}")
            return False
    
    @staticmethod
    def _generate_email_html(
        meeting_title: str,
        sender_name: str,
        summary_text: str,
        actions: List[Dict[str, Any]],
        meeting_id: int
    ) -> str:
        """Génère le contenu HTML de l'email de partage"""
        
        actions_html = ""
        if actions:
            actions_html = "<div style='margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;'>"
            actions_html += "<h3 style='color: #1f2937; font-size: 18px; font-weight: 700; margin-bottom: 15px;'>📋 Plan d'action</h3>"
            actions_html += "<ul style='margin: 0; padding: 0; list-style: none;'>"
            
            for action in actions:
                status_color = {
                    'todo': '#fbbf24',
                    'in_progress': '#60a5fa',
                    'completed': '#34d399'
                }.get(action.get('status', 'todo'), '#9ca3af')
                
                actions_html += f"""
                <li style='margin-bottom: 12px; padding: 12px; background-color: #f9fafb; border-left: 4px solid {status_color}; border-radius: 4px;'>
                    <div style='font-weight: 600; color: #1f2937;'>{action.get('description', 'N/A')}</div>
                    <div style='font-size: 12px; color: #6b7280; margin-top: 4px;'>Status: {action.get('status', 'todo').replace('_', ' ').title()}</div>
                </li>
                """
            
            actions_html += "</ul></div>"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #4b5563; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px 12px 0 0; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 24px; font-weight: 700; }}
                .content {{ background-color: white; padding: 30px; border-radius: 0 0 12px 12px; border: 1px solid #e5e7eb; border-top: none; }}
                .summary {{ background-color: #f0f4ff; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; font-size: 12px; color: #9ca3af; }}
                .btn {{ display: inline-block; padding: 12px 24px; background-color: #667eea; color: white; text-decoration: none; border-radius: 6px; font-weight: 600; margin-top: 15px; }}
                .btn:hover {{ background-color: #5568d3; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📋 {meeting_title}</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Partagé par {sender_name}</p>
                </div>
                
                <div class="content">
                    <p style="margin-top: 0;">Bonjour,</p>
                    <p>{sender_name} a partagé les détails et résultats d'analyse d'une réunion avec vous.</p>
                    
                    <div class="summary">
                        <h3 style="margin-top: 0; color: #1f2937; font-size: 16px; font-weight: 700;">📝 Résumé</h3>
                        <p style="margin: 10px 0; line-height: 1.8;">{summary_text}</p>
                    </div>
                    
                    {actions_html}
                    
                    <a href="http://localhost:3000/meetings/{meeting_id}" class="btn">
                        Voir les détails complets →
                    </a>
                    
                    <div class="footer">
                        <p>Syntra.ai - Intelligence de Réunion</p>
                        <p>© 2026 Tous droits réservés</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
