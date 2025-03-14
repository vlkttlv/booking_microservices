from fastapi import HTTPException, Request
import requests
from hotels_service.exceptions import IncorrectRoleException


def check_role(request: Request):
    access_token = request.cookies.get("booking_access_token")
    headers = {'accept': 'application/json', 'token': access_token}
    response = requests.get('http://127.0.0.1:8000/auth/me', headers=headers, timeout=10)
    if response.status_code == 401:
        raise HTTPException(status_code=401, detail="Not authorized")
    if response.json()['role'] != 'admin':
        raise IncorrectRoleException
