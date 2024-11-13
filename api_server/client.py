import json
import requests

api_db_url = 'http://localhost:5000'


def login_user(username, password, description):
    print("LOGIN USER: " + description)
    r = requests.post(
        url=api_db_url+'/login',
        headers={"Content-Type": "application/json"},
        data=json.dumps({"username": f'{username}',
                         "password": f'{password}'}))
    print(r.text)


if __name__ == "__main__":
    try:
        login_user('benton', 'boil', "Success")
    except Exception:
        print(
            "Something went wrong with the test. Make sure both servers are "
            "running, do not forget to empty Docker Volumes and try again.")
