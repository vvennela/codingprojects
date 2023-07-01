import socket
import threading
from _thread import *
import random



hostIP = "127.0.0.1" #sys.argv[2]
hostPort =  1234 #int(sys.argv[4])
lock = threading.Lock() 

def make_pack(source,dest,syn,ack,fin,data=""):
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


def connection(server_conn_sock):   #new connection socket for data
    try:
        while 1:
            message, client_address = server_conn_sock.recvfrom(1024)
            message = decode_msg(message)
            if message[4]==1:
                finAck = make_pack(server_conn_sock.getsockname()[1],client_address[1], 0, 1, 0, "")
                server_conn_sock.sendto(finAck, client_address)
                continue
            if message[3]==1:
                server_conn_sock.close()
                break
            
            print(message)
            pong_msg = make_pack(server_conn_sock.getsockname()[1], client_address[1], 0, 0, 0, "pong")
            server_conn_sock.sendto(pong_msg, client_address)
            
            
            
    except KeyboardInterrupt:
        fin = make_pack(server_conn_sock.getsockname()[1], client_address[1], 0, 0, 1, "")
        server_conn_sock.sendto(fin,client_address)
        message, client_address = server_conn_sock.recvfrom(1024)

        message = decode_msg(message)
        if message[3]==1:
            ack = make_pack(server_conn_sock.getsockname()[1], client_address[1], 0, 1, 0, "")
            server_conn_sock.sendto(ack,client_address)
            server_conn_sock.close()
            lock.release()
        return
            

def welcome():
    welcome_server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    welcome_server_sock.bind((hostIP,hostPort))
    print("Waiting for clients...")
    try:
        while 1:
            message, client_address = welcome_server_sock.recvfrom(1024)

            message = decode_msg(message)
            
            if message[2]==1 and message[3]==0: #check for syn
                server_port = random.randint(1024,65535)
                synAck = make_pack(hostPort, client_address[1], 1, 1, 0, server_port)
                welcome_server_sock.sendto(synAck, (client_address))
                
                
            message, client_address = welcome_server_sock.recvfrom(1024)

            server_conn_sock= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_conn_sock.bind((hostIP,server_port))
            start_new_thread(connection, (server_conn_sock,))
            if message[3]==1 and message[2]==0:
                lock.acquire()
                break
            
    except KeyboardInterrupt:
        welcome_server_sock.close()
        
start_new_thread(welcome(),)