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
    auth_token = quart.request.headers.get('Authorization')
    if auth_token is None:
        return quart.Response(
            utils.build_unauthorized_response(), status=401)
    auth_split = auth_token.split(" ")

    if auth_split[0] == "Bearer" and len(auth_split) == 2 and auth_split[1] == os.getenv('SECRET'):
        try:
            os.mkdir(utils.build_absolute_path(f'file/{uid}'))
            return quart.Response(status=200)
        except OSError as error:
            return quart.Response(utils.build_internal_server_error(), status=500)
    else:
        return quart.Response(utils.build_unauthorized_response(), status=401)


@app.route('/file/<uid>', methods=['DELETE'])
async def delete_user_library(uid):
    """
    Deletes the library associated to a specific user. That only happens
    when the user is also pretended to be removed from the system and this
    command can only come from users server.
    """
    auth_token = quart.request.headers.get('Authorization')
    if auth_token is None:
        return quart.Response(
            utils.build_unauthorized_response(), status=401)
    auth_split = auth_token.split(" ")

    if auth_split[0] == "Bearer" and len(auth_split) == 2 and auth_split[1] == os.getenv('SECRET'):
        # Try to remove the user library from the system
        if os.path.exists(utils.build_absolute_path(f'file/{uid}')):
            os.rmdir(utils.build_absolute_path(f'file/{uid}'))
            return quart.Response(status=200)
        else:
            return quart.Response(utils.build_not_found_response(), status=404)
    else:
        return quart.Response(utils.build_bad_request_response(), status=401)


@app.route('/file/<uid>', methods=['GET'])
async def list_documents(uid):
    print('hola')


if __name__ == "__main__":
    # Create file directory if it does not exist
    os.makedirs(utils.build_absolute_path('file'), exist_ok=True)
    app.run(host=os.getenv('LIBRARY_SERVER_IP'), port=int(os.getenv('LIBRARY_SERVER_PORT')))
