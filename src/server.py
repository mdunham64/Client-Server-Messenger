from threading import Thread
import socket


class Messaging(Thread):
    # -Receive messages from client
    # -Store the message
    # -Send the message to the recipient
    pass


class Server(Thread):
    # -Listens for client connections
    # -Receives message from client
    # -Store the message
    # -Send the message to the recipient
    # Store client user/pw/ip add/port #
    pass


class ClientWorker(Thread):
    # Connects to server
    # Sends messages to other clients
    # Receives messages from other clients
    pass


if __name__ == '__main__':
    # Load from JSON file
    # Start messaging service
    # Stop messaging service
    # Save to JSON file
    pass
