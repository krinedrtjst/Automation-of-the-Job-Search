import smtplib
from email.message import EmailMessage
from pathlib import Path

def enviar_aplicacao(destinatario, nome_recrutador, caminho_pdf):
    SMTP_SERVER = "smtp.gmail.com" 
    SMTP_PORT = 587
    EMAIL_REMETENTE = "karineduartejustino@gmail.com"
    SENHA = "wvrynewsebrqkmwu" 

    corpo_email = f"""Hi {nome_recrutador},

Thank you for reaching out and for your kind words about my background. I’m interested in the opportunity and would be happy to learn more.

The role sounds well aligned with my experience in AI data work, analytics, problem-solving, and Trust & Safety evaluation. I’d be glad to set up a time to discuss it further.

To help me prepare, could you share a few more details about the position—such as the role title, key responsibilities, location/remote policy, contract type, and compensation range? Please also feel free to send a scheduling link or a few time slots that work for you.

Looking forward to connecting.

Best regards,
Karine Duarte Justino
"""

    msg = EmailMessage()
    msg['Subject'] = "Data Scientist Application - Karine Duarte Justino"
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = destinatario
    msg.set_content(corpo_email)

    caminho = Path(caminho_pdf)
    if caminho.exists():
        with open(caminho, 'rb') as f:
            pdf_data = f.read()
            msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename="Karine_Duarte_Justino_Resume.pdf")
    else:
        print(f"❌ Erro: O arquivo {caminho_pdf} não foi encontrado. Rode o Tectonic primeiro!")
        return

    try:
        print(f"Enviando aplicação para {destinatario} na porta {SMTP_PORT}...")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(EMAIL_REMETENTE, SENHA)
            smtp.send_message(msg)
        print("✅ Aplicação enviada com sucesso!")
    except Exception as e:
        print(f"❌ Erro na conexão SMTP: {e}")

if __name__ == "__main__":
    enviar_aplicacao(
        destinatario="karineduartejustino@proton.me", 
        nome_recrutador="Abhishek",
        caminho_pdf="curriculo_gerado.pdf"
    )
enviar_aplicacao(
    destinatario="recrutador_real@empresa.com", 
    nome_recrutador="Nome do Recrutador",
    caminho_pdf="curriculo_gerado.pdf"
)
python scripts\enviar_aplicacao.py