from threading import Thread
import socket


class Client:
    def __init__(self, ip: str, port: int):
        self.__ip = ip
        self.__port = port
        self.__is_connected = False
        self.__client_socket = None
        self.__is_logged_in = False

    def connect(self):
        self.__client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__client_socket.connect((self.__ip, self.__port))
        self.__is_connected = True

    def send_message(self, msg: str):
        self.__client_socket.send(msg.encode("UTF-16"))

    def receive_message(self):
        return self.__client_socket.recv(1024).decode("UTF-16")

    def disconnect(self):
        self.__client_socket.close()
        self.__is_connected = False

    @property
    def is_connected(self):
        return self.__is_connected

    @property
    def is_logged_in(self):
        return self.__is_logged_in

    @is_logged_in.setter
    def is_logged_in(self, booly: bool):
        self.__is_logged_in = booly

class Client_Listener(Thread): # server worker
        def __init__(self, ip: str, port: int, backlog=5):
            super().__init__()
            self.__ip = ip
            self.__port = port
            self.__backlog = backlog
            self.__keep_running = True

        def run(self):
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((self.__ip, self.__port))
            server_socket.listen(self.__backlog)

            client_socket, client_address = server_socket.accept()
            print(f"""Listener setup, server connected from port {client_address[1]}""")

            client_socket.send("Connected to Client Listener".encode("UTF-16"))
            while self.__keep_running:
                client_message = client_socket.recv(1024).decode("UTF-16")
                print(client_message)

            client_socket.close()

            server_socket.close()

if __name__ == "__main__":
    keep_running = True
    client = Client("127.0.0.1", 11003)
    listener_port = 12000
    client_listener = Client_Listener("127.0.0.1", listener_port)

    while keep_running:
        print("=" * 80)
        print(f"""{"Main Menu":^80}""")
        print("=" * 80)
        print("1. Connect to server")
        print("2. Login")
        print("3. Send Message")
        print("4. Print Received Messages")
        print("5. Disconnect")
        option = int(input("Select option [1-5]>"))
        if option == 1:
            client.connect()  # We can ask ip/port here
            response = client.receive_message()
            print(response)
        elif option == 2:
            # login the user
            # prompt for sub menu - 1 to create user, 2 to login (prot: USR and LOG respectively)
            choice = int(input("Please enter 1 to login or 2 to create new user>"))
            if choice == 1:
                request = "LOG|"
                login = str(input("Please enter your user name>"))
                password = str(input("Please enter your password>"))
                request += login + "|" + password
                who_from = login
                client.send_message(request)
                login_response = client.receive_message()
                if login_response == "0|OK":
                    client.is_logged_in = True
                    print("Logged In")
                    client_listener.start()
                    listener_port = listener_port + 1
                else:
                    print(login_response)

            elif choice == 2:
                request = "USR|"
                login = str(input("Please enter your desired user name>"))
                password = str(input("Please enter your desired password>"))
                display_name = str(input("Please enter your desired display name>"))
                request += login + "|" + password + "|" + display_name
                client.send_message(request)
                response = client.receive_message()

        elif option == 3:
            # send message
            request = "MSG|"
            request += who_from + "|"
            msg_to = str(input("Enter the username of the recipient: "))
            request += msg_to + "|"
            the_msg = str(input("Enter the message: "))
            request += the_msg
            client.send_message(request)
            response = client.receive_message()
            print(response)

        elif option == 4:
            # print received messages
            pass
        elif option == 5:
            # send protocol OUT|OK
            client.send_message("OUT|")
            response = client.receive_message()
            print(response)
            client.disconnect()
        else:
            print("Invalid Option, try again. \n\n")