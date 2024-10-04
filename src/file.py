import json
import os
import shutil
import quart
import requests
import uuid
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
            return quart.Response(status=201)
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
            shutil.rmtree(utils.build_absolute_path(f'file/{uid}'))
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


@app.route('/file/<uid>/<filename>', methods=['PUT', 'POST'])
async def add_file(uid, filename):
    """
    Adds a file to the user's library whose uid corresponds to the one in the url and only allows
    the owner to do so. As it is stated in the practice guide if the file already exists, then it
    should be replaced with the new one.
    """
    auth_token = utils.get_access_token(quart.request.headers.get('Authorization'))
    if len(auth_token) == 0:
        return quart.Response(
            utils.build_unauthorized_response(), status=401)

    data = await quart.request.get_data()

    # Validate token communicating with the user server
    if validate_token(auth_token, uid):
        file_path = utils.build_absolute_path(f'file/{uid}/{filename}')
        try:
            with open(file_path, 'wb') as file:
                file.write(data)
            return quart.Response(status=201)
        except OSError:
            return quart.Response(utils.build_internal_server_error(), status=500)
    else:
        return quart.Response(utils.build_unauthorized_response(), status=401)


@app.route('/file/<uid>/<filename>', methods=['GET'])
async def send_file(uid, filename):
    """
    This function sends a file from the user's library whose uid coincides with the <uid> parameter
    and name coincides with the filename specified by the requester.
    """
    auth_token = utils.get_access_token(quart.request.headers.get('Authorization'))
    if len(auth_token) == 0:
        return quart.Response(
            utils.build_unauthorized_response(), status=401)

    # Validate token communicating with the user server
    if validate_token(auth_token, None):
        file_path = utils.build_absolute_path(f'file/{uid}/{filename}')
        if os.path.isfile(file_path):
            return await quart.send_file(file_path, as_attachment=True)
        else:
            return quart.Response(utils.build_not_found_response(), status=404)
    else:
        return quart.Response(utils.build_unauthorized_response(), status=401)


@app.route('/file/<uid>/<filename>', methods=['DELETE'])
async def delete_file(uid, filename):
    """
    This function deletes a file from the user's library. Only the owner of the library
    can remove files from it.
    """
    auth_token = utils.get_access_token(quart.request.headers.get('Authorization'))
    if len(auth_token) == 0:
        return quart.Response(
            utils.build_unauthorized_response(), status=401)

    # Validate token communicating with the user server
    if validate_token(auth_token, uid):
        file_path = utils.build_absolute_path(f'file/{uid}/{filename}')
        if os.path.exists(file_path):
            os.remove(file_path)
            return quart.Response(status=200)
        else:
            return quart.Response(utils.build_not_found_response(), status=404)
    else:
        return quart.Response(utils.build_unauthorized_response(), status=401)


def validate_token(auth_header, uid) -> bool:
    auth_header = auth_header.split('.')
    if len(auth_header) != 2:
        return False

    if uid is None:
        return uuid.UUID(auth_header[1]) == uuid.uuid5(uuid.UUID(os.getenv('SECRET')), auth_header[0])
    else:
        return uuid.UUID(auth_header[1]) == uuid.uuid5(uuid.UUID(os.getenv('SECRET')), uid)


if __name__ == "__main__":
    # Create file directory if it does not exist
    os.makedirs(utils.build_absolute_path('file'), exist_ok=True)
    app.run(host=os.getenv('LIBRARY_SERVER_IP'), port=int(os.getenv('LIBRARY_SERVER_PORT')))
