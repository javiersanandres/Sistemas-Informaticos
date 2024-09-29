import json
import uuid
from time import sleep
import utils

import requests

if __name__ == "__main__":
    user_url = 'http://localhost:5005/user'
    headers = {"Content-Type": "application/json"}
    data = {"name": "hola", "password": "pepe"}
    uid = uuid.uuid4()
    r = requests.put(url=user_url,
                     headers=headers,
                     data=json.dumps(data))

    print(r.text)
    with open(utils.build_absolute_path('user/hola.json'), 'r') as file:
        data = json.load(file)

    access_token = str(data['access_token'])
    r = requests.delete(url=user_url+'/hola', headers={'Authorization': f'Bearer {access_token}'})
    print(r.text)
    sleep(2)

