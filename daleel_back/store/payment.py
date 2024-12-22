# import requests
# from django.conf import settings

# class InstaPayClient:
#     def __init__(self):
#         self.api_key = settings.INSTAPAY_API_KEY
#         self.secret_key = settings.INSTAPAY_SECRET_KEY
#         self.base_url = settings.INSTAPAY_BASE_URL

#     def create_payment(self, amount, currency, user_details, redirect_url):
#         """
#         Create a payment request.
#         """
#         url = f"{self.base_url}/payments/create"
#         payload = {
#             "amount": amount,
#             "currency": currency,
#             "user_details": user_details,  # e.g., {"name": "John Doe", "email": "john@example.com"}
#             "redirect_url": redirect_url,
#         }
#         headers = {
#             "Authorization": f"Bearer {self.api_key}",
#             "Content-Type": "application/json",
#         }

#         response = requests.post(url, json=payload, headers=headers)
#         if response.status_code == 200:
#             return response.json()  # Return payment URL or details
#         else:
#             raise Exception(f"Error: {response.json().get('message', 'Payment creation failed')}")

#     def verify_payment(self, payment_id):
#         """
#         Verify payment status.
#         """
#         url = f"{self.base_url}/payments/{payment_id}/verify"
#         headers = {
#             "Authorization": f"Bearer {self.api_key}",
#         }

#         response = requests.get(url, headers=headers)
#         if response.status_code == 200:
#             return response.json()  # Return payment details
#         else:
#             raise Exception(f"Error: {response.json().get('message', 'Payment verification failed')}")
