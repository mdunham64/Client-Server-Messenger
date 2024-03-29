import json
from threading import Thread
import socket


class User:
    def __init__(self, rport=0):
        self.__username = None
        self.__password = None
        self.__display_name = None
        self.port_number_receive = rport
        self.port_number_broadcast = None
        self.ip = None
        self.message_list = []

    @property
    def username(self):
        return self.__username

    @username.setter
    def username(self, name):
        self.__username = name

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, password):
        self.__password = password

    @property
    def display_name(self):
        return self.__display_name

    @display_name.setter
    def display_name(self, display_name):
        self.__display_name = display_name


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
        self.__user_list = []
        self.__messages_to_relay = {"": []}
        self.stored_messages = {"": []}

    @property
    def list_cw(self):
        return self.__list_cw

    @property
    def user_list(self):
        return self.__user_list

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
                user.ip = client_address[0]
                cw = ClientWorker(client_socket, self, user)
                self.list_cw.append(cw)
                # each clientworker will be one port, but a client will have 2 ports open, one for sending, one receiving
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
        self._send_message("Connected to Messenger Service")

        while self.__keep_running_client:
            self._process_client_request()

        self.__client_socket.close()

    def terminate_connection(self):
        self.__keep_running_client = False
        self.__client_socket.close()

    def _display_message(self, message: str):
        print(f" {message}")

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

                for u in self.__server.user_list:
                    if u.username == arguments[1]:
                        checker = True

                if checker:
                    response = "1|This user name already exists"
                else:
                    new_user = User()
                    new_user.username = arguments[1]
                    new_user.password = arguments[2]
                    new_user.display_name = arguments[3]
                    self.__server.user_list.append(new_user)
                    response = "0|OK"

                self._send_message(response)

            elif arguments[0] == "LOG":  # LOG|USERNAME|PASSWORD
                # enter user credential information, differentiate ports
                logged_in_checker = False
                credential_checker = False
                for c in self.__server.list_cw:
                    if c.user.username == arguments[1]:
                        logged_in_checker = True
                for u in self.__server.user_list:
                    if u.username == arguments[1]:
                        if u.password == arguments[2]:
                            credential_checker = True
                if logged_in_checker:
                    response = "2|Already Logged In"
                    self._send_message(response)
                    return
                if credential_checker:
                    response = "0|OK"
                    self.__user.username = arguments[1]
                    self.__user.password = arguments[2]
                    self._send_message(response)
                    return
                if not credential_checker:
                    response = "1|Invalid Credentials"
                    self._send_message(response)
                    return
            elif arguments[0] == "OUT":  # OUT|OK
                response = "0|OK"
                self.__keep_running_client = False
                self.__server.list_cw.remove(self)
                self._send_message(response)
            elif arguments[0] == "MSG":  # MSG|USERNAME_FROM|USERNAME_TO|MESSAGE
                for u in self.__server.user_list:
                    if arguments[2] == u.username:
                            msg_deliverable = arguments[3] + " - From:  " + arguments[1]
                            if arguments[2] in self.__server.stored_messages:
                                self.__server.stored_messages[arguments[2]].append(msg_deliverable)
                                response = "0|message was received/stored successfully"
                                self._send_message(response)
                                return
                            else:
                                self.__server.stored_messages[arguments[2]] = []
                                self.__server.stored_messages[arguments[2]].append(msg_deliverable)
                                response = "0|message was received/stored successfully"
                                self._send_message(response)
                                return
                response = "2|No Target User"
                self._send_message(response)
                print(self.__server.stored_messages)

            elif arguments[0] == "PRM":
                response = "Your Messages: \n"
                if arguments[1] in self.__server.stored_messages:
                    popped_strings = self.__server.stored_messages.pop(arguments[1])
                    response += ' \n '.join(popped_strings)
                    self._send_message(response)
                else:
                    response = "No New Messages"
                    self._send_message(response)

            else:
                response = "ERR|Unknown Command."
                pass

        except ValueError as ve:
            response = "ERR|" + str(ve)


if __name__ == '__main__':
    server = Server("127.0.0.1", 11003, 5)
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
            the_list = []
            with open('userlist.json') as f:
                for jsonObj in f:
                    user_dict = json.loads(jsonObj)
                    the_list.append(user_dict)
                for entry in the_list:
                    new_user = User()
                    new_user.username = entry['_User__username']
                    new_user.password = entry['_User__password']
                    new_user.message_list = entry['message_list']
                    server.user_list.append(new_user)
            with open("pending_messages.json", "r") as f:
                for jsonObj in f:
                    server.stored_messages = json.loads(jsonObj)
        elif option == 2:
            try:
                server.start()
            except:
                raise RuntimeError("Server already started.")
        elif option == 3:
            server.terminate_server()
        elif option == 4:
            # Save users to file
            empty = ""
            f = open("userlist.json", "w")
            f.write(empty)
            f.close()
            for u in server.user_list:
                with open('userlist.json', 'a') as json_users:
                    json.dump(u.__dict__, json_users)
                    json_users.write("\n")
            #save pending messages to file
            with open("pending_messages.json", "w") as f:
                json.dump(server.stored_messages, f)
        else:
            print("Invalid option, try again. \n\n")
