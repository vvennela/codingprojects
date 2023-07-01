import socket
from datetime import datetime
import time


hostIP = "127.0.0.1" 
hostPort =  1234 
server_port = 0
newPort = []
#f=open("clientLog2.txt", "a")
#g=open("serverLog2.txt", "a")
        
def make_pack(source,dest,syn,ack,fin,data):
    pack = '{0:016b}'.format(source) + '{0:016b}'.format(dest) + '{0:01b}'.format(syn) + '{0:01b}'.format(ack) + '{0:01b}'.format(fin) + str(data)
    return pack.encode('utf-8')

def decode_msg(message):
    message    = message.decode('utf-8')
    source     = int(message[:16],2)
    dest       = int(message[16:32],2)
    syn        = int(message[32])
    ack        = int(message[33])
    fin        = int(message[34])
    data       = message[35:]
    message = [source, dest, syn, ack, fin, data]
    return message

def clientlog(message):
    ts=datetime.now()
    length=len(message)
    x=decode_msg(message)
    if x[2]==1 and x[3]==0:
        typ="SYN"
    if x[2]==1 and x[3]==1:
        typ="SYN/ACK"
        length-=5
    if x[2]==0 and x[3]==1:
        typ="ACK"
    if x[4]==1:
        typ="FIN"
    if x[5]=="ping" or x[5]=="pong":
        typ="DATA"
    '''with open("clientLog.txt", "a") as f:
        fcntl.flock(f, fcntl.LOCK_UN)
        f.write(f"{x[0]} | {x[1]} | {typ} | {length} | {ts}\n")
        fcntl.flock(f, fcntl.LOCK_UN)'''
    
def serverlog(message):
    ts=datetime.now()
    length=len(message)
    x=decode_msg(message)
    if x[2]==1 and x[3]==0:
        typ="SYN"
    if x[2]==1 and x[3]==1:
        typ="SYN/ACK"
    if x[2]==0 and x[3]==1:
        typ="ACK"
    if x[4]==1:
        typ="FIN"
    if x[5]=="ping" or x[5]=="pong":
        typ="DATA"
    '''with open("serverLog2.txt", "a") as g:
        fcntl.flock(g, fcntl.LOCK_UN)
        g.write(f"{x[0]} | {x[1]} | {typ} | {length} | {ts}\n")
        fcntl.flock(g, fcntl.LOCK_UN)'''

def connection(server_port):
    client_conn_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        ping_msg = make_pack(newPort[0], server_port, 0, 0, 0, "ping")
        serverlog(ping_msg)
        client_conn_sock.sendto(ping_msg, (hostIP,server_port))
        while 1:
            message, server_address = client_conn_sock.recvfrom(1024)
            clientlog(message)
            time.sleep(0.5)
            message = decode_msg(message)
            
            if message[4]==1:
                finAck = make_pack(client_conn_sock.getsockname()[1],server_address[1], 0, 1, 0, "")
                serverlog(finAck)
                client_conn_sock.sendto(finAck, server_address)
                continue
            if message[3]==1:
                client_conn_sock.close()
                break
            print(message)
            ping_msg = make_pack(client_conn_sock.getsockname()[1], server_address[1], 0, 0, 0, "ping")
            serverlog(ping_msg)
            client_conn_sock.sendto(ping_msg, server_address) 
            
                   
    except KeyboardInterrupt:
        fin = make_pack(client_conn_sock.getsockname()[1], server_address[1], 0, 0, 1, "")
        serverlog(fin)
        client_conn_sock.sendto(fin,server_address)
        message, server_address = client_conn_sock.recvfrom(1024)
        clientlog(message)
        message = decode_msg(message)
        if message[3]==1:
            ack = make_pack(client_conn_sock.getsockname()[1], server_address[1], 0, 1, 0, "")
            serverlog(ack)
            client_conn_sock.sendto(ack,server_address)
            client_conn_sock.close()
        
def welcome():
    welcome_client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    syn = make_pack(0, 0, 1, 0, 0, "")
    serverlog(syn)
    welcome_client_sock.sendto(syn, (hostIP, hostPort))
    message, server_address = welcome_client_sock.recvfrom(1024)
    clientlog(message)
    message = decode_msg(message)
    server_port = int(message[5])
    if message[2]==1 and message[3]==1:
        ack=make_pack(welcome_client_sock.getsockname()[1],server_address[1], 0, 1, 0, "")
        serverlog(ack)
        newPort.append(welcome_client_sock.getsockname()[1])
        welcome_client_sock.sendto(ack,server_address)
        welcome_client_sock.close()
    connection(server_port)
   

welcome()