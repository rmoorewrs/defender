import json
import random
import time
from datetime import datetime

from flask import Flask, Response, render_template, stream_with_context

application = Flask(__name__)
random.seed()  # Initialize the random number generator


@application.route('/')
def index():
    return render_template('index.html')


@application.route('/chart-data')
def chart_data():
    def generate_random_data():
        while True:
            xval = random.random() * 100
            yval = random.random() * 100
            json_data = json.dumps(
                [{'x' : xval, 'y': yval}])
            yield f"data:{json_data}\n\n"
            time.sleep(1)


    response = Response(stream_with_context(generate_random_data()), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response


if __name__ == '__main__':
    application.run(debug=True, threaded=True)