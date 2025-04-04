import requests
from datetime import datetime, timedelta
import time

def test_guest_system():
    base_url = 'http://localhost:5000/api'
    
    print("Test Case 1: New Guest Registration")
    # Add new guest
    response1 = requests.post(f'{base_url}/add_guest',
        files={'image': open('face.jpg', 'rb')},
        data={
            'name': 'Fares Hossam',
            'end_date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
        }
    )
    print(response1.json())

    print("\nTest Case 2: Validate Pending Guest")
    response2 = requests.post(f'{base_url}/validate_face',
        files={'image': open('face_valid.png', 'rb')}
    )
    print(response2.json())

    print("\nTest Case 3: Allow Guest")
    response3 = requests.post(f'{base_url}/validate_face',
        files={'image': open('face_valid.png', 'rb')},
        data={'status': 'allowed'}
    )
    print(response3.json())

    print("\nTest Case 4: Try to Allow Again")
    response4 = requests.post(f'{base_url}/validate_face',
        files={'image': open('face_valid.png', 'rb')},
        data={'status': 'allowed'}
    )
    print(response4.json())

    print("\nTest Case 5: Create New Invitation")
    response5 = requests.post(f'{base_url}/add_guest',
        files={'image': open('face_valid.png', 'rb')},
        data={
            'name': 'Fares Hossam2',
            'end_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        }
    )
    print(response5.json())

if __name__ == "__main__":
    test_guest_system()