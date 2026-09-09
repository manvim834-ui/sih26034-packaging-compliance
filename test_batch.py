import requests

url = "http://127.0.0.1:8000/batch"

files = [
    ("files", open("backend/test_image.jpg", "rb")),
    ("files", open("backend/test_image.jpg", "rb")),
]

data = {"product_id": "p1"}

response = requests.post(url, data=data, files=files)
print(response.status_code)
print(response.json())
