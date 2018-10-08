TCP file transfer with framing

How to run:

1. Open up bash and travel to this directory (or wherever the sourcecode files lie).
2. In the command line, type "chmod -x [filename.py]" to make the files executable (stammerProxy.py, myClient.py, myServer.py).
3. (optional) Run the stammerProxy by typing "./stammerProxy.py"
4. Run the server by typing "./myServer.py"
5. Run the client by typing "./myClient.py"

Notes:

1. The client and server work with and without the proxy.
2. The server can support multiple clients at one time.
3. If an empty file is sent, the client/server is notified through the command line.
4. If one attempts to send a flie which does not exist in the directory where the client or server lie, the client/server is notified through the command line.
5. If the file already exists on the server, the server rejects the file. If the client attempts to recieve a file from the server, that already exists in the directory specified, the client will be warned that retrieving the file will overwrite the file in that directory.
6. If the client or server disconnect, they go into a loop, in which they wait for the other to connect again.
7. In the client, a user can use the "put" or "get" commands, followed by the directory of a file to send or receive, respectively.

From the original READ-ME:

1. In stammerProxy.py, use "-?" for help.

2. In myClient.py or myServer.py, use "-?" to print parameters and default values.