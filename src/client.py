import json
import uuid
from time import sleep
import utils

import requests

user_url = 'http://localhost:5005/user'
library_url = 'http://localhost:5010/file'


def create_user(username):
    print("CREATING USER:\n")
    r = requests.put(url=user_url,
                     headers= {"Content-Type": "application/json"},
                     data=json.dumps({"name": f'{username}', "password": "pepe"}))
    print(r.text)


def delete_user(access_token, username):
    print("DELETE USER:\n")
    r = requests.delete(url=user_url + f'/{username}', headers={'Authorization': f'Bearer {access_token}'})
    print(r.text)


def create_user_library(access_token, uid):
    print("TRY TO CREATE LIBRARY DIRECTLY:\n")
    r = requests.put(url=library_url + f'/{uid}', headers={'Authorization': f'Bearer {access_token}'})
    print(r.text)


def delete_user_library(access_token, uid):
    print("TRY TO DELETE LIBRARY DIRECTLY:\n")
    r = requests.delete(url=library_url + f'/{uid}', headers={'Authorization': f'Bearer {access_token}'})
    print(r.text)


def list_user_library(access_token, uid):
    print("LIST LIBRARY:\n")
    r = requests.get(url=library_url + f'/{uid}', headers={'Authorization': f'Bearer {access_token}'})
    print(r.text)


def add_file(access_token, uid, filename, content):
    print(f"ADDING FILE {filename}:\n")
    r = requests.put(url=library_url + f'/{uid}/{filename}', headers={'Authorization': f'Bearer {access_token}'}, data=content)
    print(r.text)


def remove_file(access_token, uid, filename):
    print(f"DELETING FILE {filename}:\n")
    r = requests.delete(url=library_url + f'/{uid}/{filename}', headers={'Authorization': f'Bearer {access_token}'})
    print(r.text)


def download_file(access_token, uid, filename):
    print(f"DOWNLOADING FILE {filename}:\n")
    r = requests.get(url=library_url + f'/{uid}/{filename}', headers={'Authorization': f'Bearer {access_token}'})
    print(r.text)


if __name__ == "__main__":
    username1 = "hola1"
    username2 = "hola2"
    create_user(username1)
    create_user(username2)

    with open(utils.build_absolute_path(f'user/{username1}.json'), 'r') as file:
        data = json.load(file)

    access_token1 = str(data['uid'])+'.'+str(data['access_token'])
    uid1 = str(data['uid'])

    with open(utils.build_absolute_path(f'user/{username2}.json'), 'r') as file:
        data = json.load(file)

    access_token2 = str(data['uid'])+'.'+str(data['access_token'])
    uid2 = str(data['uid'])

    create_user_library(access_token1, uid1)
    delete_user_library(access_token1, uid1)
    list_user_library(access_token1, uid1)
    list_user_library(access_token2, uid1)

    delete_user(access_token1, username1)
    create_user(username1)
    with open(utils.build_absolute_path(f'user/{username1}.json'), 'r') as file:
        data = json.load(file)

    access_token1 = str(data['uid'])+'.'+str(data['access_token'])
    uid1 = str(data['uid'])

    add_file(access_token1, uid1, "example1.txt", "This is an example1.")
    add_file(access_token1, uid1, "example2.txt", "This is an example2.(first version")
    add_file(access_token1, uid1, "example2.txt", "This is an example2.(second version)")
    add_file(access_token2, uid1, "dummy", "dummy")
    list_user_library(access_token1, uid1)
    list_user_library(access_token2, uid1)
    remove_file(access_token2, uid1, "example1.txt")
    remove_file(access_token1, uid1, "example1.txt")
    download_file(access_token2, uid1, "example2.txt")
    download_file(access_token1, uid1, "example2.txt")