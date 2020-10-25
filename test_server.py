from flask import Flask, make_response, request
import requests


app = Flask(__name__)

ALL_METHODS = ["GET", "POST"]


def load_file(file):
    with open(file, "r") as fileh:
        return fileh.read()


@app.route("/<path:path>", methods=ALL_METHODS)
def hello(path):
    return load_file("test_response.xml")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10301, debug=True)
