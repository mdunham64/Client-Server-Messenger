from threading import Thread

class User(Thread):
    def __init__(self):
        _username = None
        _password = None
        _ip_address = None
        _port_number = None
    # Needs to be able to create user
    # Needs to be able to sign in
    # be able to connect to server
    # be able to send/rcv messages

    pass

class Client(Thread):
    pass
    # to listen for servers response messages.
    # Connect to server and send messages
    # THIS NEEDS TO BE UNIQUE PORT NUMBER FOR SERVER TO SEND TO.

class Client_Server:
    pass
    # to listen for servers incoming messages from others.
    # THIS NEEDS TO BE UNIQUE PORT NUMBER FOR SERVER TO SEND TO.


