import datetime
import threading
import atexit
from flask import Flask

# Multithreading implementation borrowed from this SO post:
# https://stackoverflow.com/questions/14384739/how-can-i-add-a-background-thread-to-flask

POOL_TIME = 1 #Seconds

# variables that are accessible from anywhere
commonDataStruct = []
# lock to control access to variable
dataLock = threading.Lock()
# thread handler
thread = threading.Thread()

def start_node():
    app = Flask(__name__)

    @app.route('/test', methods=['GET'])
    def recieve_test():
        print('--- API REQUEST RECIEVED ---')
        return 'Nice'

    def stop_processing():
        global thread
        thread.cancel()

    def process_tx():
        global commonDataStruct
        global thread
        with dataLock:
        # Do your stuff with commonDataStruct Here
            print('! ! ! DOING THE NEXT THING ! ! !', datetime.datetime.now())

        # Set the next thread to happen
        thread = threading.Timer(POOL_TIME, process_tx, ())
        thread.start()   

    def begin_processing():
        # Do initialisation stuff here
        global thread
        # Create your thread
        thread = threading.Timer(POOL_TIME, process_tx, ())
        thread.start()

    # Initiate
    begin_processing()
    # When you kill Flask (SIGTERM), clear the trigger for the next thread
    atexit.register(stop_processing)
    return app.run(debug=True, use_reloader=False)

app = start_node()
