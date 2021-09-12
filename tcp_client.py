#!/usr/bin/env python3

import socket
import pickle
from table import Table


class Client:
    def __init__(self, host, port, size):
        self.host = host       # Server's connection IPv4 address
        self.port = port       # Server's connection port
        self.size = size       # Socket's data size (bytes)
        self.hostname = "N/A"  # Client's hostname
        self.server = "N/A"    # Server's hostname

    def run(self):
        try:
            # Create client's TCP socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_client:
                # Successful socket connection
                tcp_client.connect((self.host, self.port))
                # Get client's hostname
                self.hostname = socket.gethostname()
                # Receive & print initial data from server
                response = tcp_client.recv(self.size)
                self.server = response.decode()
                print(self.server)
                # Send client data to server
                tcp_client.sendall(self.hostname.encode())
                # Start infinite loop for multiple queries
                while True:
                    # Get query from the client
                    client_query = str(input("\n[~] SQL query: "))
                    if client_query == "quit":
                        # Send quit query & exit infinite loop
                        tcp_client.sendall(client_query.encode())
                        break
                    # Send query to the server
                    tcp_client.sendall(client_query.encode())
                    # Receive & print query's result data from server
                    server_response = tcp_client.recv(self.size)
                    if not server_response:
                        print("[-] Nothing Received. The Server may be logged out. Connection will close, Goodbye!")
                        break
                    print("\n[+] Received: ")
                    # Get query result
                    table_data = pickle.loads(server_response)
                    Table.show(table_data)
                # Close the client's socket connection
                print("\n[-] Client {0} logged out.\n[~] Goodbye!".format(self.hostname))
                tcp_client.close()
        except socket.error as err:
            # Print exception
            print("\n[-] {0}".format(err))


if __name__ == "__main__":
    # Client's main configuration
    HOST = "127.0.0.1"                 # Server's connection IPv4 address
    PORT = 9753                        # Server's connection port
    SIZE = 5120                        # Socket's data size (bytes)
    client = Client(HOST, PORT, SIZE)  # New Client object
    client.run()                       # Start client's operation
