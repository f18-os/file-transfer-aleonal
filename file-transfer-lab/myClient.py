#! /usr/bin/env python3
import socket, sys, re
sys.path.append("../lib")       # for params
import params
from mySock import framedSend, framedReceive

global s

def connectSocket():
    global s
    switchesVarDefaults = (
        (('-s', '--server'), 'server', "127.0.0.1:50001"),
        (('-d', '--debug'), "debug", False), # boolean (set if present)
        (('-?', '--usage'), "usage", False), # boolean (set if present)
        )


    progname = "framedClient"
    paramMap = params.parseParams(switchesVarDefaults)
    server, usage, debug  = paramMap["server"], paramMap["usage"], paramMap["debug"]


    if usage:
        params.usage()


    try:
        serverHost, serverPort = re.split(":", server)
        serverPort = int(serverPort)
    except:
        print("Can't parse server:port from '%s'" % server)
        sys.exit(1)


    for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        try:
            print("creating sock: af=%d, type=%d, proto=%d" % (af, socktype, proto))
            s = socket.socket(af, socktype, proto)
        except socket.error as msg:
            print(" error: %s" % msg)
            s = None
            continue
        try:
            print("attempting to connect to %s" % repr(sa))
            s.connect(sa)
        except socket.error as msg:
            print(" error: %s" % msg)
            s.close()
            s = None
            continue
        break


    if s is None:
        print('could not open socket')
        sys.exit(1)

def fileTransfer(prompt):
    global s
    if "exit" in prompt:
        print("Closing connection...")
        framedSend(s, b"sdsf", 1)
        s.close()
        sys.exit(0)

    command, file = re.split(" ", prompt)
    f = None

    if "put" in command:
        try:
            f = open(file, "rb")
        except FileNotFoundError:
            print("File not found.")
            return

        data = command.encode() + b" " + file.encode() + b" " + f.read()
        f.close()
        framedSend(s, data, -1)

        print("File sent.")
    elif "get" in command:
        data = command.encode() + b" " + file.encode()
        framedSend(s, data, -1)
        print("File request sent.")

        data = framedReceive(s, -1)
        f = open(file, "wb")
        f.write(data)
        f.close()
        print("File received.")
    else:
        print("Unknown command.")

if __name__ == '__main__':
    global s
    connectSocket()
    while True:
        prompt = input("Enter command and filename, or 'exit' to disconnect: ")
        fileTransfer(prompt)

    s.close()
