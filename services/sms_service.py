import requests
import re
import os


class SMSService:
    def __init__(self, app=None):
        self.api_key = None
        self.username = None
        self.sender_id = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize with Flask app config"""
        self.api_key = app.config.get("AFRICASTALKING_API_KEY")
        self.username = app.config.get("AFRICASTALKING_USERNAME", "sandbox")
        self.sender_id = app.config.get("SMS_SENDER_ID", "MAIZE-DISEASE")

    def format_phone_number(self, phone_number):
        """Format Tanzanian phone numbers to international format"""
        phone = re.sub(r"\D", "", str(phone_number))

        if phone.startswith("0"):
            phone = "255" + phone[1:]
        elif phone.startswith("255") and len(phone) == 12:
            pass
        elif not phone.startswith("255"):
            phone = "255" + phone

        return phone

    def send_sms(self, phone_number, message):
        """
        Send SMS using Africa's Talking API
        Returns: (success: bool, result: str)
        """
        if not self.api_key:
            return False, "SMS API key not configured"

        try:
            formatted_number = self.format_phone_number(phone_number)

            url = "https://api.africastalking.com/version1/messaging"

            headers = {
                "apiKey": self.api_key,
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            }

            data = {
                "username": self.username,
                "to": formatted_number,
                "message": message,
                "from": self.sender_id,
            }
            response = requests.post(url, headers=headers, data=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                if result.get("SMSMessageData", {}).get("Recipients"):
                    recipient = result["SMSMessageData"]["Recipients"][0]
                    if recipient.get("status") == "Success":
                        return True, f"SMS sent successfully to {formatted_number}"
                    else:
                        return (
                            False,
                            f"Failed: {recipient.get('status', 'Unknown error')}",
                        )
                else:
                    return False, "No recipients in response"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"

        except requests.exceptions.Timeout:
            return False, "SMS service timeout"
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to SMS service"
        except Exception as e:
            print(f"SMS Error: {str(e)}")
            return False, str(e)

    def send_approval_sms(self, officer_name, phone_number, region):
        """Send approval SMS to extension officer"""
        message = f"""CONGRATULATIONS {officer_name}!

Your Extension Officer application has been APPROVED!

✅ You can now:
• Login to your account
• Assist farmers with disease diagnosis
• Access training materials

Region: {region}

Login: http://localhost:5000/login

- Maize Disease Detection Team"""

        return self.send_sms(phone_number, message)

    def send_rejection_sms(self, officer_name, phone_number, reason):
        """Send rejection SMS to extension officer"""
        message = f"""Dear {officer_name},

Your Extension Officer application has been REJECTED.

Reason: {reason}

Contact support for more information.

- Maize Disease Detection Team"""

        return self.send_sms(phone_number, message)


class DebugSMSService:
    """Mock SMS service for development/testing - NO REAL SMS SENT"""

    def send_sms(self, phone_number, message):
        print("=" * 50)
        print(f"📱 SMS WOULD BE SENT TO: {phone_number}")
        print(f"📝 MESSAGE:")
        print(message)
        print("=" * 50)
        return True, "Debug mode - SMS not actually sent"

    def send_approval_sms(self, officer_name, phone_number, region):
        print("=" * 50)
        print(f"✅ APPROVAL SMS FOR: {officer_name}")
        print(f"📱 TO: {phone_number}")
        print(f"📍 REGION: {region}")
        print("=" * 50)
        return True, "Debug mode - SMS not actually sent"

    def send_rejection_sms(self, officer_name, phone_number, reason):
        print("=" * 50)
        print(f"❌ REJECTION SMS FOR: {officer_name}")
        print(f"📱 TO: {phone_number}")
        print(f"📝 REASON: {reason}")
        print("=" * 50)
        return True, "Debug mode - SMS not actually sent"
