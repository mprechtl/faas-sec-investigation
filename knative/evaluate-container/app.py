import os

from flask import Flask
import container

app = Flask(__name__)

@app.route('/')
def evaluate_container():
    return container.evaluate("/home/function", "text.txt", "Test")

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))
