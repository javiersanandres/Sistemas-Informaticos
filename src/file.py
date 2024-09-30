import json
import os
import uuid

import quart
import requests
from dotenv import load_dotenv

import utils

app = quart.Quart(__name__)

load_dotenv()


@app.route('/file/<uid>', methods=['PUT'])
async def create_user_library(uid):
    """
        Creates a library associated to a specific user. This action can only
        be commanded by the users server. Any other attempt will be rejected.
    """
    auth_token = utils.get_access_token(quart.request.headers.get('Authorization'))
    if len(auth_token) == 0 or auth_token != os.getenv('SECRET'):
        return quart.Response(
            utils.build_unauthorized_response(), status=401)
    else:
        try:
            os.mkdir(utils.build_absolute_path(f'file/{uid}'))
            return quart.Response(status=200)
        except OSError:
            return quart.Response(utils.build_internal_server_error(), status=500)


@app.route('/file/<uid>', methods=['DELETE'])
async def delete_user_library(uid):
    """
    Deletes the library associated to a specific user. That only happens
    when the user is also pretended to be removed from the system and this
    command can only come from users server.
    """
    auth_token = utils.get_access_token(quart.request.headers.get('Authorization'))
    if len(auth_token) == 0 or auth_token != os.getenv('SECRET'):
        return quart.Response(
            utils.build_unauthorized_response(), status=401)
    else:
        # Try to remove the user library from the system
        if os.path.exists(utils.build_absolute_path(f'file/{uid}')):
            os.rmdir(utils.build_absolute_path(f'file/{uid}'))
            return quart.Response(status=200)
        else:
            return quart.Response(utils.build_not_found_response(), status=404)


@app.route('/file/<uid>', methods=['GET'])
async def list_documents(uid):
    """
    Lists the library associated to a user. It will return a 401 Unauthorized Response
    if anybody but the user tries to list the library
    """
    auth_token = utils.get_access_token(quart.request.headers.get('Authorization'))
    if len(auth_token) == 0:
        return quart.Response(
            utils.build_unauthorized_response(), status=401)

    # Validate token communicating with the user server
    if validate_token(auth_token, uid):
        try:
            files = os.listdir(utils.build_absolute_path(f'file/{uid}'))
            return quart.Response(response=utils.build_html_list_of_files(files))
        except FileNotFoundError:
            return quart.Response(utils.build_not_found_response(), status=404)
    else:
        return quart.Response(utils.build_unauthorized_response(), status=401)


def validate_token(auth_token, uid) -> bool:
    try:
        request = requests.get(
            url='http://' + os.getenv('USERS_SERVER_IP') + ':' + os.getenv(
                'USERS_SERVER_PORT') + f'/user/{uid}' ,
            headers={"Authorization": 'Bearer ' + str(os.getenv('SECRET')),
                     "Content-Type": "application/json"},
            data=json.dumps({"access_token" : f'{auth_token}'})
        )

        if request.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.ConnectionError:
        return False


if __name__ == "__main__":
    # Create file directory if it does not exist
    os.makedirs(utils.build_absolute_path('file'), exist_ok=True)
    app.run(host=os.getenv('LIBRARY_SERVER_IP'), port=int(os.getenv('LIBRARY_SERVER_PORT')))
