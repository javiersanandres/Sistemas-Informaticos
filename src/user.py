import json
import os
import uuid

import quart
import requests
from dotenv import load_dotenv

import utils

load_dotenv()
app = quart.Quart(__name__)


@app.route('/user', methods=['PUT'])
async def register_user():
    """
    Registers a new user.
    """
    data_json = await quart.request.get_json()

    # Fetch user data from request body
    try:
        username = data_json['name']
        password = data_json['password']
    except KeyError as e:
        html_response = utils.build_bad_request_response(
            f'Missing field: {str(e)}')
        return quart.Response(html_response, status=400)
    except TypeError as e:
        return quart.Response(utils.build_bad_request_response(), status=400)

    # Generate user UUID and access token
    user_uuid, access_token = generate_user_uuid_and_access_token()

    # Generate file with user's info
    try:
        generate_user_file(username, password,
                           user_uuid, access_token)
    except ValueError as e:
        html_response = utils.build_bad_request_response(str(e))
        return quart.Response(html_response, status=400)

    # Generate user's library
    user_creation_failure = generate_user_library(user_uuid)
    if user_creation_failure:
        if os.path.exists(
                utils.build_absolute_path(
                    f'user/{username}.json')):
            os.remove(
                utils.build_absolute_path(
                    f'user/{username}.json'))

        return quart.Response(utils.build_internal_server_error(), status=500)

    return quart.jsonify({"uid": user_uuid, "access_token": access_token})


@app.route('/user', methods=['GET'])
async def login_user():
    """
    Returns a user's credentials on a successful login.
    """
    data_json = await quart.request.get_json()

    # Fetch user data from request body
    try:
        username = data_json['name']
        password = data_json['password']
    except KeyError as e:
        html_response = utils.build_bad_request_response(
            f'Missing field: {str(e)}')
        return quart.Response(html_response, status=400)
    except TypeError as e:
        return quart.Response(
            utils.build_bad_request_response(
                f'Missing user name and password.'),
            status=400)

    # Fetch user's credentials from file
    try:
        user_uuid, access_token = get_user_credentials(username, password)
    except ValueError as e:
        html_response = utils.build_bad_request_response(str(e))
        return quart.Response(html_response, status=400)

    return quart.jsonify({"uid": user_uuid, "access_token": access_token})


@app.route('/user/<username>', methods=['DELETE'])
async def delete_user(username):
    """
    Deletes an already registered user. This function also deletes the library
    associated to that user by using SAGA pattern.
    """
    auth_token = quart.request.headers.get('Authorization')
    if auth_token is None:
        return quart.Response(
            utils.build_unauthorized_response(), status=401)

    auth_split = auth_token.split(" ")

    if auth_split[0] != "Bearer" or len(auth_split) != 2:
        return quart.Response(utils.build_bad_request_response(), status=400)

    try:
        with open(utils.build_absolute_path('user/' + username + '.json'), 'r') as file:
            data = json.load(file)
        access_token = str(data['access_token'])

        if access_token != auth_split[1]:
            return quart.Response(
                utils.build_unauthorized_response(), status=401)
        
        # Try first to delete the library associated
        # If there were no answer from the other server, the user
        # would still be in the system
        library_url = 'http://' + os.getenv('LIBRARY_SERVER_IP') + ':' + os.getenv(
            'LIBRARY_SERVER_PORT') + f'/file/' + str(data['uid'])
            
        request = requests.delete(
            url=library_url,
            headers={"Authorization": 'Bearer ' + str(os.getenv('SECRET'))})
        if request.status_code != 200:
            return quart.Response(status=500)
            
        # Finally remove the user from the system
        if os.path.exists(
                utils.build_absolute_path(
                    f'user/{username}.json')):
            os.remove(
                utils.build_absolute_path(
                    f'user/{username}.json'))
            return quart.Response(
                'User successfully deleted', status=200)
        else:
            return quart.Response(status=404)
    except requests.exceptions.ConnectionError:
        return quart.Response(
            utils.build_internal_server_error(), status=500)
    except OSError:
        return quart.Response(utils.build_not_found_response(), status=404)


@app.route('/user/<uid>', methods=['GET'])
async def validate_token(uid):
    """
    If uid is not an empty string, it checks whether the access_token sent corresponds to the uid
    specified. If the uid is the empty string, then it just checks whether the access_token belongs
    to a user in the system.
    """
    auth_token = utils.get_access_token(
        quart.request.headers.get('Authorization'))
    if len(auth_token) == 0 or auth_token != os.getenv('SECRET'):
        return quart.Response(
            utils.build_unauthorized_response(), status=401)

    try:
        data = await quart.request.get_json()
        token_for_validation = str(data['access_token'])
    except (KeyError, TypeError, ValueError):
        return quart.Response(utils.build_unauthorized_response(), status=401)

    user_dir = utils.build_absolute_path("user")
    # Iterate through all JSON files in the user directory
    for filename in os.listdir(user_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(user_dir, filename)
            try:
                with open(file_path, 'r') as f:
                    user_data = json.load(f)

                if user_data.get('access_token') == token_for_validation:
                    if uid != "" and user_data.get('uid') == uid:
                        return quart.Response(status=200)
                    elif uid == " ":
                        return quart.Response(status=200)
                    else:
                        return quart.Response(utils.build_unauthorized_response(), status=401)

            except (json.JSONDecodeError, OSError, KeyError, TypeError, ValueError):
                continue

    # If no match was found, return unauthorized response
    return quart.Response(utils.build_unauthorized_response(), status=401)


def generate_user_uuid_and_access_token() -> tuple:
    """
    Generates a user's UUID and access token.
    """
    user_uuid = uuid.uuid4()
    secret_uuid = uuid.UUID(os.getenv('SECRET'))
    access_token = uuid.uuid5(secret_uuid, str(user_uuid))

    return user_uuid, access_token


def generate_user_file(username: str,
                       password: str,
                       user_uuid: uuid.UUID,
                       access_token: uuid.UUID) -> None:
    """
    Generates a file with the user's info.
    """
    filepath = utils.build_absolute_path(f'user/{username}.json')

    # Check if user already exists
    if os.path.isfile(filepath):
        raise ValueError(f'The user \'{username}\' already exists.')

    # Dump data to file as JSON
    user_data = {"username": username,
                 "password": password,
                 "uid": str(user_uuid),
                 "access_token": str(access_token)}
    with open(filepath, 'w') as f:
        json.dump(user_data, f)


def generate_user_library(user_uuid: uuid.UUID) -> bool:
    """
    Generates a user's library by requesting the library service.
    """
    user_creation_failure = False
    try:
        request = requests.put('http://' +
                               os.getenv('LIBRARY_SERVER_IP') +
                               ':' +
                               os.getenv('LIBRARY_SERVER_PORT') +
                               f'/file/{str(user_uuid)}', headers={"Authorization": 'Bearer ' +
                                                                   str(os.getenv('SECRET'))})
        user_creation_failure = request.status_code != 201
    except requests.exceptions.ConnectionError:
        user_creation_failure = True

    return user_creation_failure


def get_user_credentials(username: str,
                         password: str) -> tuple:
    """
    Returns the user's credentials fetched from the correct file.
    """
    filepath = utils.build_absolute_path(f'user/{username}.json')

    # Check if user exists and if the given password is correct
    try:
        with open(filepath, 'r') as f:
            user_data = json.load(f)
            read_password = user_data['password']
    except FileNotFoundError:
        raise ValueError(f'User \'{username}\' is not registered.')
    
    if read_password != password:
        raise ValueError(f'Incorrect username or password')
    
    return (uuid.UUID(user_data['uid']),
            uuid.UUID(user_data['access_token']))


if __name__ == "__main__":
    # Create user directory if it does not exist
    os.makedirs(utils.build_absolute_path('user'), exist_ok=True)
    app.run(host=os.getenv('USERS_SERVER_IP'),
            port=int(os.getenv('USERS_SERVER_PORT')))
