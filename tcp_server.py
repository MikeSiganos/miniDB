#!/usr/bin/env python3

import socket
import threading
from datetime import datetime
from database import Database
import pickle


class Client(threading.Thread):
    def __init__(self, host, port, connection, size, db):
        threading.Thread.__init__(self)  # Client's thread
        self.host = host                 # Server's connection IPv4 address
        self.port = port                 # Server's connection port
        self.connection = connection     # Client's socket connection
        self.size = size                 # Socket's data size (bytes)
        self.db = db                     # Database
        self.hostname = "N/A"            # Client's hostname
        self.server = "N/A"              # Server's hostname

    def initialize_client(self):
        # Start infinite loop for multiple requests
        while True:
            # Get query from client
            client_query = self.connection.recv(self.size).decode()
            try:
                # Split client's query on space character
                split_client_query = client_query.split(" ")
                # Mini SQL compiler only for SELECT queries
                db_result = self.db.select(split_client_query[3], split_client_query[1], return_object=True)
                # Send query results to the client
                self.connection.sendall(pickle.dumps(db_result))
                # Close client connection
                # print("[-] Client {0} ({1}:{2}) logged out.".format(self.hostname, self.host, self.port))
                # self.connection.close()
            except Exception as ex:
                # Send exception data on client & close connection
                self.connection.sendall(str(ex).encode())
                print("[-] Client {0} ({1}:{2}) logged out.".format(self.hostname, self.host, self.port))
                self.connection.close()
                break

    def run(self):
        try:
            # Receive data from the client
            client_data = self.connection.recv(self.size)
            # Set client's hostname
            self.hostname = client_data.decode()
            # Handle DB request from client
            self.initialize_client()
        except socket.error as err:
            # Close client's connection & print exception
            print("[-] Client {0} ({1}:{2}) logged out.".format(self.hostname, self.host, self.port))
            print("[-] {0}".format(err))
            if self.connection:
                self.connection.close()


class Server:
    def __init__(self, host, port, size):
        self.host = host                       # Server's IPv4 address
        self.port = port                       # Server's operation port
        self.size = size                       # Socket's data size (bytes)
        self.hostname = "N/A"                  # Server's hostname
        self.address = (self.host, self.port)  # Server's address = [host IP, Port]
        self.server = None                     # Server's socket
        self.clients = []                      # Server's clients list
        self.db = None                         # Database

    def initialize_server(self):
        try:
            # Create server's TCP socket
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Get server's hostname
            self.hostname = socket.gethostname()
            # Bind network's configuration (IP host & port) with the created socket
            self.server.bind(self.address)
            # Enable server's socket listening
            self.server.listen(5)
            # Print welcome message & server's status on startup
            print("\n[+] Welcome! Starting TCP server | Listening on {0}:{1}\n"
                  "\n[~] Loading DB & Waiting for clients...".format(self.host, self.port))
            # Load database
            self.db = Database("smdb", load=True)
        except socket.error as serv_conn_err:
            # Close server's connection & print exception
            print("[-] Server {0} ({1}) logged out.\n[~] Goodbye!".format(self.hostname, self.host))
            print("[-] {0}".format(serv_conn_err))
            if self.server:
                self.server.close()

    def run(self):
        # Initialize server
        self.initialize_server()
        try:
            # Start infinite loop
            while True:
                # Get server's time stamp
                curr_date_time = "{0:%A} {0:%d} {0:%B} {0:%Y} {0:%H}:{0:%M}:{0:%S}".format(datetime.now())
                # Accept client's connections
                client_connection, address = self.server.accept()
                # Print client's socket info on successful connection
                print("\n[+] New connection: {0}:{1} ({2})".format(address[0], address[1], curr_date_time))
                # Create a Client object & Pass it's main configuration
                client = Client(address[0], address[1], client_connection, self.size, self.db)
                # Send welcome message & server's info to client
                if client.server == "N/A":
                    client.server = self.hostname
                server_response = "[+] {0} Successfully connected with the server ({1}). Welcome!". \
                    format(curr_date_time, self.hostname)
                client.connection.sendall(server_response.encode())
                # Start client's thread & Request a query
                client.start()
                # Append new client to the clients list
                self.clients.append(client)
            # self.server.close()
        except socket.error as serv_err:
            # Close server's connection & print exception
            print("[-] Server {0} ({1}) logged out.\n[~] Goodbye!".format(self.hostname, self.host))
            print("[-] {0}".format(serv_err))
            if self.server:
                self.server.close()


if __name__ == "__main__":
    # Server's main configuration
    HOST = "127.0.0.1"                 # Local IPv4 address
    PORT = 9753                        # Local empty port
    SIZE = 5120                        # Socket's data size (bytes)
    server = Server(HOST, PORT, SIZE)  # New Server object
    server.run()                       # Start server's operation
