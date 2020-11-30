from threading import Thread
import socket


class User:
    def __init__(self, rport: int):
        self.username = None
        self.password = None
        self.display_name = None
        self.port_number_receive = rport
        self.port_number_broadcast = None
        self.message_list = []

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, name):
        self.__username = name

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = password

    @property
    def display_name(self):
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        self._username = display_name


class Server(Thread):
    def __init__(self, ip: str, port: int, backlog: int):
        super().__init__()
        self.__ip = ip
        self.__port = port
        self.__backlog = backlog
        self.__server_socket = None
        self.__keep_running = True
        self.__connection_count = 0
        self.__list_cw = []

    @property
    def list_cw(self):
        return self.__list_cw

    def run(self):
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_socket.bind((self.__ip, self.__port))
        self.__server_socket.listen(self.__backlog)

        while self.__keep_running:
            print(f"""[SRV] Waiting for Client""")
            try:
                client_socket, client_address = self.__server_socket.accept()
                self.__connection_count += 1
                print(f"""[SRV] Got a connection from {client_address}""")
                user = User(client_address[1])
                cw = ClientWorker(client_socket, self, user)
                # each clientworker will be one port, but a client will have 2 ports open, one for sending, one receiving
                self.__list_cw.append(cw)
                cw.start()
            except Exception as e:
                print(e)

        cw: ClientWorker
        for cw in self.__list_cw:
            cw.terminate_connection()
            cw.join()

    def terminate_server(self):
        self.__keep_running = False
        self.__server_socket.close()


class ClientWorker(Thread):
    def __init__(self, client_socket: socket, server: Server, user: User):
        super().__init__()
        self.__client_socket = client_socket
        self.__keep_running_client = True
        self.__server = server
        self.__user = user

    @property
    def user(self):
        return self.__user

    def run(self):
        self._send_message("Connected to Python Library Server")

        while self.__keep_running_client:
            self._process_client_request()

        self.__client_socket.close()

    def terminate_connection(self):
        self.__keep_running_client = False
        self.__client_socket.close()

    def _display_message(self, message: str):
        print(f"CLIENT >> {message}")

    def _send_message(self, msg: str):
        self._display_message(f"""SEND>> {msg}""")
        self.__client_socket.send(msg.encode("UTF-16"))
        pass

    def _receive_message(self, max_length: int = 1024):
        msg = self.__client_socket.recv(max_length).decode("UTF-16")
        self._display_message(f"""RCV>> {msg}""")
        return msg

    def _process_client_request(self):
        client_message = self._receive_message()
        self._display_message(f"CLIENT SAID>>>{client_message}")

        arguments = client_message.split("|")
        response = ""

        try:
            if arguments[0] == "USR":  # USR|USERNAME|PASSWORD|DISPLAY_NAME
                checker = False

                for cw in self.__server.list_cw:
                    if cw.__user.username == arguments[1]:
                        checker = True

                if checker:
                    response = "1|This user name already exists"
                else:
                    self.user.username = arguments[1]
                    self.user.password = arguments[2]
                    self.user.display_name = arguments[3]
                    response = "0|OK, user created."

                self._send_message(response)

            elif arguments[0] == "LOG":  # LOG|USERNAME|PASSWORD
                self.__user.username(arguments[1])
                self.__user.password(arguments[2])
                # enter user credential information, differeniate ports
                response = "0|OK"
                self._send_message(response)
            elif arguments[0] == "OUT":  # OUT|OK
                response = "0|OK"
                self.__keep_running_client = False
                self._send_message(response)
            elif arguments[0] == "MSG":  # MSG|USERNAME_FROM|USERNAME_TO|MESSAGE

                response = "0|OK"
            else:
                response = "ERR|Unknown Command."
                pass

        except ValueError as ve:
            response = "ERR|" + str(ve)


if __name__ == '__main__':
    server = Server("127.0.0.1", 10000, 5)
    dontexit = True
    while dontexit:
        print("=" * 80)
        print(f"""{"Main Menu":^80}""")
        print("=" * 80)
        print("1. Load data from file")
        print("2. Start the messenger service")
        print("3. Stop the messenger service")
        print("4. Save data to file")
        print("-" * 80)
        option = int(input("Select option [1-4]>"))
        if option == 1:
            # load data from file (STORE THIS as server to override it)
            pass
        elif option == 2:
            try:
                server.start()
            except:
                raise RuntimeError("Server already started.")
        elif option == 3:
            server.terminate_server()
            dontexit = False
        elif option == 4:
            # Save data to file
            pass
        else:
            print("Invalid option, try again. \n\n")
