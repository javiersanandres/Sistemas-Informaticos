import requests
import json
import uuid

user_url = 'http://localhost:5000/user'
headers = {"Content-Type": "application/json"}
data = {"name":"hola"}
uid = uuid.uuid4()
r = requests.put(url=user_url,
                 headers=headers,
                 data=json.dumps(data))

print(r)
print(r.text)