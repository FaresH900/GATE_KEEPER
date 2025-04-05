import requests
import time

BASE_URL = 'http://localhost:5000/auth'

def test_auth_flows():
    # Test variables
    admin_credentials = {
        'email': 'hossam@admin.com',
        'password': 'password123'
    }
    resident_credentials = {
        'email': 'hossam@resident.com',
        'password': 'password123'
    }

    def login(credentials):
        response = requests.post(f'{BASE_URL}/login', json=credentials)
        print(f"\nLogin Response ({credentials['email']}):", response.json())
        return response.json() if response.status_code == 200 else None

    def check_token(token):
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f'{BASE_URL}/check_token', headers=headers)
        print("Token Check Response:", response.json())
        return response.status_code == 200

    def logout(token):
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.post(f'{BASE_URL}/logout', headers=headers)
        print("Logout Response:", response.json())
        return response.status_code == 200

    # Test 1: Admin Login -> Check Token -> Logout -> Check Token
    print("\n=== Testing Admin Flow ===")
    admin_tokens = login(admin_credentials)
    if admin_tokens:
        print("\nTesting valid token...")
        token_check = check_token(admin_tokens['access_token'])
        print(f"Token valid: {token_check}")
        assert token_check == True
        
        print("\nLogging out...")
        logout_success = logout(admin_tokens['access_token'])
        print(f"Logout successful: {logout_success}")
        assert logout_success == True
        
        print("\nTesting token after logout...")
        token_check = check_token(admin_tokens['access_token'])
        print(f"Token should be invalid: {not token_check}")
        assert not token_check

    # Test 2: Resident Login
    print("\n=== Testing Resident Flow ===")
    resident_tokens = login(resident_credentials)
    if resident_tokens:
        print("\nTesting valid token...")
        token_check = check_token(resident_tokens['access_token'])
        print(f"Token valid: {token_check}")
        assert token_check == True

        print("\nLogging out...")
        logout_success = logout(resident_tokens['access_token'])
        print(f"Logout successful: {logout_success}")
        assert logout_success == True

    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    test_auth_flows()