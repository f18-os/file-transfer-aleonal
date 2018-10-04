#! /usr/bin/env python3
import socket, sys, re, time
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

def fileTransfer(prompt):
    global s
    if "exit" in prompt:
        print("Closing connection...")
        framedSend(s, b"sdsf", 1)
        s.close()
        sys.exit(0)

    if " " in prompt:
        command, file = re.split(" ", prompt)
    else:
        print("Unknown command.")
        return


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

        if "sdsf" in data.decode():
            print("File already exists on server, file was rejected!");
            return

        print("File sent.")
    elif "get" in command:
        isFound = 0
        data = command.encode() + b" " + file.encode()

        try:
            open(file, "rb")
        except FileNotFoundError:
            isFound = 1

        if isFound == 0:
            print("File already exists in directory. Retrieving file from server will overwrite file.")
            print("Are you sure you want to continue? (yes/no)")
            if "yes" in input():
                pass
            elif "no" in input():
                print("File retrieval aborted.")
                return
            else:
                print("Wrong command, file retrieval aborted.")
                return

        framedSend(s, data, -1)
        print("File request sent.")
        data = framedReceive(s, -1)
        if checkServerStatus(data) == -2: return -2

        if "sdsf" in data.decode():
            print("Error, file not found in server.");
            return
        elif "empty" in data.decode():
            print("Error, file in server was empty. File not retrieved.")
            return

        f = open(file, "wb")
        f.write(data)
        f.close()
        print("File received.")
    else:
        print("Unknown command.")

def checkServerStatus(data):
    if not data:
        print("Server abruptly disconnected!")
        return -2

if __name__ == '__main__':
    global s
    s = None
    while True:
        while not s:
            print("Wait...")
            time.sleep(3)
            connectSocket()

        while True:
            prompt = input("Enter command and filename, or 'exit' to disconnect: ")
            result = fileTransfer(prompt)
            if result == -2: break
            print()

        s.close()
        s = None
