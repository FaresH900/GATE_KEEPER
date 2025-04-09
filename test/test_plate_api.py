import requests
import os

def test_api():
    try:
        # Configuration
        url = 'http://localhost:5000/api/recognize'
        image_path = 'test.jpg'  # Ensure this file exists in the current directory
        headers = {}

        # Check if image exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file '{image_path}' not found")

        # Optional: Add CSRF token if your Flask app requires it
        # Assuming your app uses 'X-CSRF-TOKEN' header (from gatekeeper_dashboard.html)
        session = requests.Session()
        login_url = 'http://localhost:5000/auth/check_token'  # Adjust if different
        session.get(login_url)  # Fetch session cookies
        csrf_token = session.cookies.get('csrf_access_token')  # Match your cookie name
        if csrf_token:
            headers['X-CSRF-TOKEN'] = csrf_token
            print(f"Using CSRF token: {csrf_token}")
        else:
            print("No CSRF token found; proceeding without it (may fail if required)")

        # Prepare the file for upload
        with open(image_path, 'rb') as f:
            files = {'image': (os.path.basename(image_path), f, 'image/jpeg')}
            # Send POST request
            response = session.post(url, files=files, headers=headers)

        # Check response status
        response.raise_for_status()  # Raises an exception for 4xx/5xx errors

        # Print JSON response
        print("Response from /api/recognize:")
        print(response.json())

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"HTTP Error: {e}")
        if e.response is not None:
            print(f"Response content: {e.response.text}")
    except ValueError as e:
        print(f"JSON Decode Error: {e} (Response may not be JSON)")
        print(f"Raw response: {response.text}")
    except AttributeError as e:
        print(f"Attribute Error: {e} (Check exception handling)")
    except Exception as e:
        print(f"Unexpected Error: {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    test_api()