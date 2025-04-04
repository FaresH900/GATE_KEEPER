# # test_facial_api.py
# import requests
# import base64

# def test_add_guest():
#     url = 'http://localhost:5000/api/add_guest'
    
#     # Test with file upload
#     with open('face.jpg', 'rb') as f:
#         files = {
#             'image': ('face.jpg', f, 'image/jpeg'),
#         }
#         data = {'name': 'Fares Hossam'}
#         response = requests.post(url, files=files, data=data)
#         print("Add Guest Response:", response.json())

# def test_validate_face():
#     url = 'http://localhost:5000/api/validate_face'
    
#     # Test with file upload
#     with open('face_valid.png', 'rb') as f:
#         files = {'image': ('face_valid.png', f, 'image/png')}
#         response = requests.post(url, files=files)
#         print("Validate Face Response:", response.json())

# if __name__ == "__main__":
#     test_add_guest()
#     test_validate_face()

# test_facial_api.py
import requests

def test_add_new_guest():
    url = 'http://localhost:5000/api/add_guest'
    with open('face.jpg', 'rb') as f:
        files = {'image': ('face.jpg', f, 'image/jpeg')}
        data = {'name': 'Fares Hossam'}
        response = requests.post(url, files=files, data=data)
        print("Add New Guest:", response.json())

def test_validate_and_update():
    url = 'http://localhost:5000/api/validate_face'
    with open('face_valid.png', 'rb') as f:
        files = {'image': ('face_valid.png', f, 'image/png')}
        data = {'status': 'allowed'}  # Optional status update
        response = requests.post(url, files=files, data=data)
        print("Validate Face:", response.json())

if __name__ == "__main__":
    test_add_new_guest()
    test_validate_and_update()