
# INSTRUCTIONS FOR RUNNING
You can start the program by running the server.py file. <br />
You must load from the files before staring the messenger service. If you run the messenger service without loading from file,<br> create users, and
then save, you will overwrite the pre-loaded users.<br>
Then you may run the client.py as many times are you would like.
<br />
<br />
To create a new user there is a sub menu under the login option on the client main menu.<br>
You may also choose to login with a pre-loaded User. Here is your login info:<br>
username: Oleksiy <br>
password: 3920 <br>
<br />
We encourage you to fire up a few clients, login, send messages around, load some messages, don't load some, save and<br>
safely shut down the server. Feel free to re-run, log in, and load undelivered messages and just keep playing with it. <br>
You will see everything is functional and works correctly as outlined in the assignment.<br>

Programmers:<br>
MacGyver Dunham<br>
Jake Bush<br>
Ronald Jenkins<br>
Savannah Murphy<br>
# server.py functionality 
#### Below is a breakdown of each class and its purpose: 
`User:`
<br />
This class creates the necessary information to keep track of each user. It includes
a username, password, display name, send request port, receive request port, and a message
list. This information is passed to the ClientWorker so each ClientWorker has an identifiable
user.

`Server(Threaded):`
<br />
Server establishes the messenger service and acts as the main hub for the program. As such, it will hold
all relevant information such as lists of users, lists of ClientWorkers, and lists of pending messages.
This object is started in the main thread of server.py. While running, the server will accept new
clients and create an associated clientworker for them.

`ClientWorker(Threaded):`
<br />
ClientWorker will process the requests of each client independently. This is where error handling occurs
and the handling of client requests.

# client.py functionality
#### Below is a breakdown of each class and its purpose:
`Client:`
<br />
Client establishes the connection to the server for the send request information. This is the class that will be 
sending requests to the ClientWorker for handling.

`Client_Listener(Threaded):`
<br />
Client_Listener acts as a "server" for the client. This is where the server will relay messages to the active
user on this client. It will hold a list of messages ready to be printed, and continuously listen for incoming messages.
