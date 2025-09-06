import requests

BASE_URL = "http://127.0.0.1:8000"

# 1️⃣ Register a user
register_data = {
    "username": "latika",
    "email": "latika@example.com",
    "password": "mypassword"
}

register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
print("Register Response:", register_response.json())

# 2️⃣ Login to get JWT token
login_data = {
    "username": "latika@example.com",  # note: username field is email in OAuth2PasswordRequestForm
    "password": "mypassword"
}

login_response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
print("Login Response:", login_response.json())

# Extract token
token = login_response.json().get("access_token")
if not token:
    print("Login failed. Cannot get token.")
    exit()

# 3️⃣ Access protected route
headers = {"Authorization": f"Bearer {token}"}
profile_response = requests.get(f"{BASE_URL}/users/me", headers=headers)
print("Protected Route Response:", profile_response.json())