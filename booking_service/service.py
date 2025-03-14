from fastapi import HTTPException, Request
import requests

def get_current_user(request: Request):
    access_token = request.cookies.get("booking_access_token")
    headers = {'accept': 'application/json', 'token': access_token}
    user_response = requests.get('http://127.0.0.1:8000/auth/me', headers=headers)
    if user_response.status_code == 401:
        raise HTTPException(status_code=401, detail="Not authorized")
    return user_response.json()