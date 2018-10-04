#! /usr/bin/env python3
import sys
sys.path.append("../lib")       # for params
import os, socket, params, re


switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

debug, listenPort = paramMap['debug'], paramMap['listenPort']

if paramMap['usage']:
    params.usage()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
bindAddr = ("127.0.0.1", listenPort)
lsock.bind(bindAddr)
lsock.listen(5)
print("listening on:", bindAddr)

while True:
    sock, addr = lsock.accept()

    from mySock import framedSend, framedReceive

    if not os.fork():
        print("new child process handling connection from", addr)

        while True:
            payload = framedReceive(sock, debug)

            if not payload:
                print("Client in port %s abruptly disconnected. Ending child process." % addr[1])
                sys.exit(0)

            if "sdsf" in payload.decode():
                print("Client in port %s exiting..." % addr[1])
                sys.exit(0)

            data = re.split(" ", payload.decode())

            if "put" in data[0]:
                if not open(data[1], "rb"):
                    f = open(data[1], "wb")
                    f.write(data[2])
                    f.close()
                    print("File received.")
                else:
                    print("File already exists in server!")
                    framedSend(sock, b"sdsf", 1)

            elif "get" in data[0]:
                print("File request received.")

                try:
                    f = open(data[1], "rb")
                except FileNotFoundError:
                    print("File not found.")
                    framedSend(sock, b"sdsf", 1)
                    continue

                if os.stat(data[1]).st_size == 0:
                    framedSend(sock, b"empty", -1)
                    f.close()
                    print("Error, file is empty.")
                    continue

                framedSend(sock, f.read(), -1)
                f.close()
                print("File sent.")

            if debug: print("rec'd: ", payload)
