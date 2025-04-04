import requests

def test_api():
    try:
        url = 'http://localhost:5000/api/recognize'
        files = {'image': open('test.jpg', 'rb')}
        response = requests.post(url, files=files)
        print(response.json())
    except Exception as e:
        print(f'{e.message}')

if __name__ == "__main__":
    test_api()