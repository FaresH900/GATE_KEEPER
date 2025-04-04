import requests

BASE_URL = 'http://localhost:5000/auth'

def test_auth():
    # Login test
    login_data = {
        'email': 'admin@example.com',
        'password': 'admin123'
    }
    response = requests.post(f'{BASE_URL}/login', json=login_data)
    print("Login Response:", response.json())
    
    if response.status_code == 200:
        tokens = response.json()
        headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
        
        # Test protected route
        response = requests.get(f'{BASE_URL}/me', headers=headers)
        print("User Info Response:", response.json())
        
        # Test refresh token
        refresh_headers = {'Authorization': f'Bearer {tokens["refresh_token"]}'}
        response = requests.post(f'{BASE_URL}/refresh', headers=refresh_headers)
        print("Refresh Token Response:", response.json())

if __name__ == "__main__":
    test_auth()