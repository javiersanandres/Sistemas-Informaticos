import json
import os
from dotenv import load_dotenv
import requests

load_dotenv()

api_db_url = 'http://127.0.0.1:' + os.getenv('API_SERVER_PORT')

if __name__ == "__main__":
    city = "timur"
    r = requests.delete(
        url=api_db_url + f'/borraCiudad/{city}')
    print(r.text)