from quart import Quart
import argparse
import utils
import os

app = Quart(__name__)

@app.route('/file/<uuid:UID>')
async def index(UID):
    return f'Hello, {UID}'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='file.py')
    parser.add_argument('--host', default='localhost', help='IP Address for library server.')
    parser.add_argument('-p', '--port', type=int, default='5010', help='Port number for library server')
    args = parser.parse_args()

    # Create user directory if it does not exist
    os.makedirs(utils.build_absolute_path('file'), exist_ok=True)
    app.run(host=args.host, port=args.port)