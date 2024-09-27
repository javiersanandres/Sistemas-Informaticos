import quart
import uuid
import json
import os
from dotenv import load_dotenv
import utils
import argparse

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
        html_response = utils.build_bad_request_response(f'Missing field: {str(e)}')
        return quart.Response(html_response, status=400)

    # Generate user UUID and access token
    user_uuid, access_token = generate_user_uuid_and_access_token()

    # Generate file with user's info
    try:
        generate_user_file(username, password,
                           user_uuid, access_token)
    except ValueError as e:
        html_response = utils.build_bad_request_response(str(e))
        return quart.Response(html_response, status=400)

    return quart.jsonify({"uid": user_uuid, "acces_token": access_token})


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
        html_response = utils.build_bad_request_response(f'Missing field: {str(e)}')
        return quart.Response(html_response, status=400)

    # Fetch user's credentials from file
    try:
        user_uuid, access_token = get_user_credentials(username, password)
    except ValueError as e:
        html_response = utils.build_bad_request_response(str(e))
        return quart.Response(html_response, status=400)

    return quart.jsonify({"uid": user_uuid, "access_token": access_token})


'''
@app.route('/user/<str:username>', methods=['DELETE'])
async def delete_user(username):
    """
    Deletes an already registered user. This function also deletes the library
    associated to that user by using SAGA pattern.
    """
    auth_token = quart.request.headers.get('Authorization')
    auth_split = auth_token.split(" ")
    if auth_split[0] == "Bearer":
        try:
            with open(utils.build_absolute_path('user/' + username + '.json'), 'r') as file:
                data = json.load(file)
            access_token = str(data['access_token'])
            if access_token != auth_split[1]:
                return quart.Response(utils.build_unauthorized_response(), status=401)
            else:
                # Try first to delete the library associated
                print("TODO")                         
        except:
            return quart.Response(utils.build_not_found_response(), status=404)

    else:
        return quart.Response(utils.build_bad_request_response(), status=400)
'''


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
    filepath = utils.build_absolute_path(f'user/{username}.txt')

    # Check if user already exists
    if os.path.isfile(filepath):
        raise ValueError(f'The user {username} already exists.')

    # Dump data to file as JSON
    user_data = {"username": username,
                 "password": password,
                 "uid": str(user_uuid),
                 "access_token": str(access_token)}
    with open(filepath, 'w') as f:
        json.dump(user_data, f)


def get_user_credentials(username: str,
                         password: str) -> tuple:
    """
    Returns the user's credentials fetched from the correct file.
    """
    filepath = utils.build_absolute_path(f'user/{username}.txt')

    # Check if user exists and if the given password is correct
    try:
        with open(filepath, 'r') as f:
            user_data = json.load(f)
            read_password = user_data['password']
    except:
        print('TODO')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='user.py')
    parser.add_argument('--host', default='localhost', help='IP Address for users server.')
    parser.add_argument('-p', '--port', type=int, default='5005', help='Port number for users server')
    args = parser.parse_args()

    # Create user directory if it does not exist
    os.makedirs(utils.build_absolute_path('user'), exist_ok=True)
    app.run(host=args.host, port=args.port)
