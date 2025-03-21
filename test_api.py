import requests

# API Endpoint
url = "http://127.0.0.1:5000/upload"

# File path (make sure file exists)
file_path = "health_data.json"

try:
    with open(file_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(url, files=files)

    print("Response Code:", response.status_code)
    
    # Check if the response is valid JSON before printing
    if response.headers.get('Content-Type') == 'application/json':
        print("Response Data:", response.json())
    else:
        print("Invalid response format:", response.text)

except FileNotFoundError:
    print("Error: File not found. Make sure 'health_data.json' exists in the directory.")
except requests.exceptions.ConnectionError:
    print("Error: Could not connect to the server. Make sure Flask is running.")
