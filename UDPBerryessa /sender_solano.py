import sys
import socket
from datetime import datetime 
import time


hostIP = "127.0.0.1" 
hostPort =  1234 
newPort = []
input_file = "alice29.txt" 
timeout = 0 
estimatedRTT = 0
devRTT = 0
i=0

def binarize(inputFile):
    global i 
    bytSize = []
    with open(inputFile, "r", encoding = "ascii") as inFile:
        bytes = inFile.read(920)
        while bytes:
            bytSize.append(' '.join(format(ord(x), 'b') for x in bytes))
            bytes = inFile.read(920)
        length = len(bytSize)
        if i > length-1:
            return "complete"
        data = bytSize[i]
        i+=1
    data_string = ""
    binary_values = data.split()
    for x in binary_values:
        anInt = int(x, 2)
        ascii_char = chr(anInt)
        data_string += ascii_char
    return data_string
        

def make_pack(source,dest,seqNum, ackNum, syn,ack,fin,data):
    pack = '{0:016b}'.format(source) + '{0:016b}'.format(dest) + '{0:032b}'.format(seqNum) + '{0:032b}'.format(ackNum)+ '{0:01b}'.format(syn) + '{0:01b}'.format(ack) + '{0:01b}'.format(fin) + str(data)
    return pack.encode('utf-8')

def decode_msg(message):
    message    = message.decode('utf-8')
    source     = int(message[:16],2)
    dest       = int(message[16:32],2)
    seqNum     = int(message[32:64],2)
    ackNum     = int(message[64:96],2)
    syn        = int(message[96])
    ack        = int(message[97])
    fin        = int(message[98])
    data       = message[99:]
    message = [source, dest, seqNum, ackNum, syn, ack, fin, data]
    return message

def clientlog(message):
    ts=datetime.now()
    length=len(message)
    x=decode_msg(message)
    if x[4]==1 and x[5]==0:
        typ="SYN"
    if x[4]==1 and x[5]==1:
        typ="SYN/ACK"
        length-=5
    if x[4]==0 and x[5]==1:
        typ="ACK"
    if x[6]==1:
        typ="FIN"
    if x[7]=="ping" or x[7]=="pong":
        typ="DATA"
    '''with open("clientLogpart2.txt", "a") as f:
        fcntl.flock(f, fcntl.LOCK_UN)
        f.write(f"{x[0]} | {x[1]} | {typ} | {length} | {ts}\n")
        fcntl.flock(f, fcntl.LOCK_UN)'''
    
def serverlog(message):
    ts=datetime.now()
    length=len(message)
    x=decode_msg(message)
    if x[4]==1 and x[5]==0:
        typ="SYN"
    if x[4]==1 and x[5]==1:
        typ="SYN/ACK"
    if x[4]==0 and x[5]==1:
        typ="ACK"
    if x[6]==1:
        typ="FIN"
    if x[7]=="ping" or x[7]=="pong":
        typ="DATA"
    '''with open("serverLogpart2.txt", "a") as g:
        fcntl.flock(g, fcntl.LOCK_UN)
        g.write(f"{x[0]} | {x[1]} | {typ} | {length} | {ts}\n")
        fcntl.flock(g, fcntl.LOCK_UN)'''
        
def calcTimeout(sampleRTT):
    global timeout,estimatedRTT,devRTT
    estimatedRTT = (1-.125) * estimatedRTT + .125 * sampleRTT
    devRTT = (1-.25) * devRTT + .25 * abs(sampleRTT - estimatedRTT)
    timeout = estimatedRTT + 4 * devRTT
    return 
    
    

def connection(server_port):
    client_conn_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        ping_msg = make_pack(newPort[0], server_port, 0, 0, 0, 0, 0, binarize(input_file))
        start= time.time()
        client_conn_sock.sendto(ping_msg, (hostIP,server_port))
        message, server_address = client_conn_sock.recvfrom(1024)
        end = time.time()
        rtt = end-start
        calcTimeout(rtt)

        
        while 1:
            ping_msg = make_pack(client_conn_sock.getsockname()[1], server_address[1], 0, 0, 0, 0, 0, binarize(input_file))
            start= time.time()
            client_conn_sock.sendto(ping_msg, server_address)
            print(timeout)
            client_conn_sock.settimeout(timeout) 
            ack=False
            message, server_address = client_conn_sock.recvfrom(1024)
            while not ack:
                try:
                    message, server_address = client_conn_sock.recvfrom(1024)
                    ack = True
                except socket.timeout:
                    client_conn_sock.sendto(ping_msg, server_address) 
            end = time.time()
            rtt = end-start
            calcTimeout(rtt)
            message = decode_msg(message)
            if message[6]==1:
                finAck = make_pack(client_conn_sock.getsockname()[1],server_address[1], 0, 0, 0, 1, 0, "")
                client_conn_sock.sendto(finAck, server_address)
                continue
            if message[5]==1:
                print(message)
                ack = make_pack(client_conn_sock.getsockname()[1],server_address[1], 0, 0, 0, 1, 0, "")
                client_conn_sock.sendto(ack, server_address)
                client_conn_sock.close()
                break
            print(message)
            
            
                   
    except KeyboardInterrupt:
        fin = make_pack(client_conn_sock.getsockname()[1], server_address[1], 0, 0, 0, 0, 1, "")
        #serverlog(fin)
        client_conn_sock.sendto(fin,server_address)
        message, server_address = client_conn_sock.recvfrom(1024)
        #clientlog(message)
        message = decode_msg(message)
        if message[5]==1:
            ack = make_pack(client_conn_sock.getsockname()[1], server_address[1], 0, 0, 0, 1, 0, "")
            #serverlog(ack)
            client_conn_sock.sendto(ack,server_address)
            client_conn_sock.close()
        
def welcome():
    welcome_client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    syn = make_pack(hostPort, hostPort, 0, 0, 1, 0, 0, "")
    #serverlog(syn)
    welcome_client_sock.sendto(syn, (hostIP, hostPort))
    message, server_address = welcome_client_sock.recvfrom(1024)
    #clientlog(message)
    message = decode_msg(message)
    server_port = int(message[7])
    if message[4]==1 and message[5]==1:
        ack=make_pack(welcome_client_sock.getsockname()[1],server_address[1], 0, 0, 0, 1, 0, "")
        #serverlog(ack)
        newPort.append(welcome_client_sock.getsockname()[1])
        welcome_client_sock.sendto(ack,server_address)
        welcome_client_sock.close()
    connection(server_port)
   

welcome()
