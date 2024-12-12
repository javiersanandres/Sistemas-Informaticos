import json
import os
from dotenv import load_dotenv
import requests
import sys  # Para leer parámetros desde la línea de comandos

load_dotenv()

api_db_url = 'http://127.0.0.1:' + os.getenv('API_SERVER_PORT')

if __name__ == "__main__":
    # Leer parámetros desde la línea de comandos
    if len(sys.argv) < 3:
        print("Uso: python script.py <city> <sleep>")
        sys.exit(1)

    city = sys.argv[1]
    sleep = float(sys.argv[2])  # Convertir a float para tiempo de espera

    print(f'[CLIENT] Petition to delete city {city} with sleep {sleep} seconds')

    r = requests.delete(
        url=api_db_url + f'/borraCiudad/{city}',
        headers={'Content-Type': 'application/json'},
        data=json.dumps({'wrong_order': False, 'progressive': False, 'sleep': sleep})
    )
    print(r.text)
