"""
Skill de envio de emails
"""

from .base_skill import BaseSkill
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailSkill(BaseSkill):
    """Envia emails e mensagens"""
    
    def __init__(self, lucy_memory=None):
        super().__init__(lucy_memory)
        self.description = "Envio de emails"
        self.triggers = ['email', 'mensagem', 'mandar', 'enviar']
        self.config = None
        self._load_config()
    
    def _load_config(self):
        if self.memory and 'preferences' in self.memory.data:
            self.config = self.memory.data['preferences'].get('email_config')
    
    def can_handle(self, text: str) -> bool:
        keywords = ['enviar email', 'mandar email', 'email para', 'mensagem para']
        return any(kw in text.lower() for kw in keywords)
    
    def handle(self, text: str, **kwargs) -> str:
        if not self.config:
            return self._simulate(text)
        
        to_email = self._extract_email(text)
        if not to_email:
            return "❌ Para quem devo enviar?"
        
        subject = self._extract_subject(text) or "Mensagem da Lucy"
        message = self._extract_message(text) or "Olá!"
        
        try:
            self._send(to_email, subject, message)
            return f"✅ Email enviado para {to_email}"
        except Exception as e:
            return f"❌ Erro: {e}"
    
    def _send(self, to, subject, body):
        msg = MIMEMultipart()
        msg['From'] = self.config['from_email']
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
        server.starttls()
        server.login(self.config['username'], self.config['password'])
        server.send_message(msg)
        server.quit()
    
    def _extract_email(self, text):
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        return match.group(0) if match else None
    
    def _extract_subject(self, text):
        match = re.search(r'assunto[:\s]+(.+?)(?:\s+(?:dizendo|que)|$)', text, re.I)
        return match.group(1).strip() if match else None
    
    def _extract_message(self, text):
        match = re.search(r'(?:dizendo|falando|que)\s+(.+)', text, re.I)
        return match.group(1).strip() if match else None
    
    def _simulate(self, text):
        return "📧 [Simulação] Configure email em config.py para enviar de verdade"