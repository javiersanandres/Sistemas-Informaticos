import json
import os
from dotenv import load_dotenv
import requests

load_dotenv()

api_db_url = 'http://127.0.0.1:' + os.getenv('API_SERVER_PORT')

if __name__ == "__main__":

    # Delete from a city with no customers
    print('\n\n[CLIENT] Petition to delete city \'Madrid\'')
    r = requests.delete(
        url=api_db_url + f'/borraCiudad/madrid',
        headers={'Content-Type': 'application/json'},
        data=json.dumps({'wrong_order': False, 'progressive': False, 'sleep': 0.0})
    )
    print(r.text)

    city = 'sagger'

    # Delete in wrong order
    print(f'\n[CLIENT] Petition to delete city \'{city}\' in wrong order\n')
    r = requests.delete(
        url=api_db_url + f'/borraCiudad/{city}',
        headers={'Content-Type': 'application/json'},
        data=json.dumps({'wrong_order': True, 'progressive': False, 'sleep': 0.0})
    )
    print(r.text)

    # Delete in wrong order with intermediate commits
    print(f'\n[CLIENT] Petition to delete city \'{city}\' in wrong order progressively\n')
    r = requests.delete(
        url=api_db_url + f'/borraCiudad/{city}',
        headers={'Content-Type': 'application/json'},
        data=json.dumps({'wrong_order': True, 'progressive': True, 'sleep': 0.0})
    )
    print(r.text)

    city = 'roving'

    # Delete in the correct order
    print(f'\n[CLIENT] Petition to delete city \'{city}\' correctly\n')
    r = requests.delete(
        url=api_db_url + f'/borraCiudad/{city}',
        headers={'Content-Type': 'application/json'},
        data=json.dumps({'wrong_order': False, 'progressive': False, 'sleep': 0.0})
    )
    print(r.text)