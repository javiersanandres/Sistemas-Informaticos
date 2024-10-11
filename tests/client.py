import json
import requests

user_url = 'http://localhost:5005/user'
library_url = 'http://localhost:5010/file'


def create_user(username, description=""):
    print("CREATING USER: " + description)
    r = requests.put(url=user_url,
                     headers={"Content-Type": "application/json"},
                     data=json.dumps({"name": f'{username}',
                                      "password": "pepe"}))
    print(r.text)

    if description == "(New user)":
        return json.loads(r.text)
    else:
        return None


def delete_user(access_token, username, description=""):
    print("DELETE USER: " + description)
    r = requests.delete(
        url=user_url + f'/{username}',
        headers={
            'Authorization': f'Bearer {access_token}'})
    print(r.text)


def login_user(username, password, description=""):
    print("LOGIN USER: " + description)
    r = requests.get(
        url=user_url,
        headers={"Content-Type": "application/json"},
        data=json.dumps({"name": f'{username}',
                         "password": f'{password}'}))
    print(r.text)


def create_user_library(access_token, uid):
    print("TRY TO CREATE LIBRARY DIRECTLY:")
    r = requests.put(
        url=library_url + f'/{uid}',
        headers={
            'Authorization': f'Bearer {access_token}'})
    print(r.text)


def delete_user_library(access_token, uid):
    print("TRY TO DELETE LIBRARY DIRECTLY:")
    r = requests.delete(
        url=library_url + f'/{uid}',
        headers={
            'Authorization': f'Bearer {access_token}'})
    print(r.text)


def list_user_library(access_token, uid, description=""):
    print("LIST LIBRARY: " + description)
    r = requests.get(
        url=library_url + f'/{uid}',
        headers={
            'Authorization': f'Bearer {access_token}'})
    print(r.text)


def add_file(access_token, uid, filename, content, description=""):
    print(f"ADDING FILE {filename}: " + description)
    r = requests.put(
        url=library_url + f'/{uid}/{filename}',
        headers={
            'Authorization': f'Bearer {access_token}'},
        data=content)
    print(r.text)


def remove_file(access_token, uid, filename, description=""):
    print(f"DELETING FILE {filename}: " + description)
    r = requests.delete(
        url=library_url + f'/{uid}/{filename}',
        headers={
            'Authorization': f'Bearer {access_token}'})
    print(r.text)


def download_file(access_token, uid, filename, description=""):
    print(f"DOWNLOADING FILE {filename}: " + description)
    r = requests.get(
        url=library_url + f'/{uid}/{filename}',
        headers={
            'Authorization': f'Bearer {access_token}'})
    print(r.text)


if __name__ == "__main__":
    username1 = "hola1"
    username2 = "hola2"

    try:
        data = create_user(username1, "(New user)")
        access_token1 = str(data['uid']) + '.' + str(data['access_token'])
        uid1 = str(data['uid'])

        data = create_user(username2, "(New user)")
        access_token2 = str(data['uid']) + '.' + str(data['access_token'])
        uid2 = str(data['uid'])

        create_user(username1, "(Already existing user)")

        login_user(username1, "pepe", "(Valid credentials)")
        login_user(username1, "jose", "(Invalid credentials)")
        login_user("hola", "Pepe", "(Non-existing user)")

        create_user_library(access_token1, uid1)
        delete_user_library(access_token1, uid1)

        list_user_library(access_token1, uid1, "(Valid access token)")
        list_user_library(access_token2, uid1, "(Invalid access token)")

        delete_user(access_token1, username1, "(Existing user)")
        delete_user(access_token1, username1, "(Non-existing user)")

        data = create_user(username1, "(New user)")
        access_token1 = str(data['uid']) + '.' + str(data['access_token'])
        uid1 = str(data['uid'])

        add_file(access_token1, uid1, "example1.txt", "This is an example1.\n",
                 description="(Valid access token)")
        add_file(access_token1, uid1, "example2.txt",
                 "This is an example2.(first version)\n",
                 description="(Valid access token)")
        add_file(
            access_token1,
            uid1,
            "example2.txt",
            "This is an example2.(second version)\n",
            description="(Valid access token but already existing file)")
        add_file(access_token2, uid1, "dummy", "dummy",
                 description="(Invalid access token)")

        list_user_library(access_token1, uid1, "(Valid access token)")
        list_user_library(access_token2, uid1, "(Invalid access token)")

        remove_file(access_token2, uid1, "example1.txt",
                    description="(Invalid access token)")
        remove_file(access_token1, uid1, "example1.txt",
                    description="(Invalid access token)")

        download_file(
            access_token2,
            uid1,
            "example2.txt",
            description="(Existing file but not from user's own library)")
        download_file(
            access_token1,
            uid1,
            "example2.txt",
            description="(Existing file and from user's own library)")
        download_file(access_token1, uid1, "example1.txt",
                      description="(Non-existing file)")

    except Exception:
        print(
            "Something went wrong with the test. Make sure both servers are "
            "running, do not forget to empty Docker Volumes and try again.")
