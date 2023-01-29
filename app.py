from flask import Flask

from publisher import start_listener, my_object

start_listener()

app = Flask(__name__)

@app.route('/')
def hello():
    return f"my_object vale {my_object.attr_1}"
