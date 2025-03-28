import requests
import base64

url = "http://localhost:8000/evaluate_json/"

with open("birth_1.jpg", "rb") as f:
    file_base64 = base64.b64encode(f.read()).decode('utf-8')

payload = {
    "file_base64": file_base64,
    "component_name": "свидетельство"
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())