import sys
import socket
import threading
from _thread import *
import random
import time

hostIP = "127.0.0.1" 
hostPort =  1234 
output_file = "output.txt" 
packet_loss = 10 
jitter = 0.5 
binary_file = ""
lock = threading.Lock() 



def send_ack():#use: if send_ack() -> sock.sendto(ackpack)
    x = random.randint(0, 100)
    if x<= packet_loss:
        return False
    else:
        return True
    
def jitter_test():
    x = round(random.uniform(0, 1), 1)
    if x>jitter:
        time.sleep(x)
    return

""" def binary2string(data):
    data_string = ""
    binary_values = data.split()
    for x in binary_values:
        anInt = int(x, 2)
        ascii_char = chr(anInt)
        data_string += ascii_char
    return data_string """

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


def connection(server_conn_sock):   #new connection socket for data
    global binary_file
    try:
        while 1:
            message, client_address = server_conn_sock.recvfrom(1024)
            message = decode_msg(message)
            if message[6]==1:#KEEP
                finAck = make_pack(server_conn_sock.getsockname()[1],client_address[1], 0, 0, 0, 1, 0, "")
                server_conn_sock.sendto(finAck, client_address)
                continue
            if message[5]==1:#KEEP
                server_conn_sock.close()
                f=open(output_file,"w")
                f.write(binary_file)
                break
            if message[7] == "complete":
                finAck = make_pack(server_conn_sock.getsockname()[1],client_address[1], 0, 0, 0, 1, 0, "")
                server_conn_sock.sendto(finAck, client_address)
                continue
            if send_ack():
                print(message)
                binary_file = binary_file + message[7]
                jitter_test
                pong_msg = make_pack(server_conn_sock.getsockname()[1], client_address[1], 0, 0, 0, 0, 0, "")
                server_conn_sock.sendto(pong_msg, client_address)
            
            
    except KeyboardInterrupt: #KEEP
        fin = make_pack(server_conn_sock.getsockname()[1], client_address[1], 0, 0, 0, 0, 1, "")
        server_conn_sock.sendto(fin,client_address)
        message, client_address = server_conn_sock.recvfrom(1024)

        message = decode_msg(message)
        if message[5]==1:
            ack = make_pack(server_conn_sock.getsockname()[1], client_address[1], 0, 0, 0, 1, 0, "")
            server_conn_sock.sendto(ack,client_address)
            server_conn_sock.close()
            lock.release()
        return
            

def welcome():
    welcome_server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    welcome_server_sock.bind((hostIP,hostPort))
    print("Listening for client...")
    try:
        while 1:
            message, client_address = welcome_server_sock.recvfrom(1024)
            message = decode_msg(message)
            if message[4]==1 and message[5]==0: #check for syn
                server_port = random.randint(1024,65535)
                synAck = make_pack(hostPort, client_address[1], 0, 0, 1, 1, 0, server_port)
                welcome_server_sock.sendto(synAck, (client_address))
                
                
            message, client_address = welcome_server_sock.recvfrom(1024)

            server_conn_sock= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_conn_sock.bind((hostIP,server_port))
            start_new_thread(connection, (server_conn_sock,))
            if message[5]==1 and message[4]==0:
                lock.acquire()
                break
            
    except KeyboardInterrupt:
        welcome_server_sock.close()


        
start_new_thread(welcome(),)