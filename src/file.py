from quart import Quart

app = Quart(__name__)

@app.route('/file/<uuid:UID>')
async def index(UID):
    return f'Hello, {UID}'

app.run()