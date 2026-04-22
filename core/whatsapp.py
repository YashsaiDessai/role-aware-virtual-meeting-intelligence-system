import os
import logging
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def send_whatsapp_summary(gemma_output: str) -> None:
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    
    if not account_sid or not auth_token:
        logger.error("Twilio credentials not configured in environment.")
        return

    client = Client(account_sid, auth_token)

    try:
        message = client.messages.create(
            body=gemma_output,
            from_='whatsapp:+14155238886',
            to='whatsapp:+919359611406'
        )
        logger.info(f"Summary sent! SID: {message.sid}")
    except Exception as error:
        logger.error(f"Failed to send WhatsApp: {error}")
