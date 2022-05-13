import socket
import sys
import time
import json
import struct

# set defaults for muticast
MC_PORT=5007
RECV_NIC_IP="0.0.0.0"
MC_GROUP_ADDRESS="224.1.1.5"
MC_PORT=5007

def help_and_exit(prog):
    print('Usage: ' + prog + ' send <server_ip> <server_port>', file=sys.stderr)
    print('   or: ' + prog + ' recv', file=sys.stderr)
    sys.exit(1)

def multicast_send(send_nic_ip, msgbuf):
    sender = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM,proto=socket.IPPROTO_UDP, fileno=None)
    multicast_grp = (MC_GROUP_ADDRESS, MC_PORT)
    sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)

    sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF,socket.inet_aton(send_nic_ip))
    sender.sendto(msgbuf, multicast_grp)
    sender.close()

def multicast_recv(recv_nic_ip, multicast_grp_ip, multicast_port):
    bufsize = 1024

    receiver = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, \
            proto=socket.IPPROTO_UDP, fileno=None)
    bindaddr = (multicast_grp_ip, multicast_port)
    receiver.bind(bindaddr)

    if recv_nic_ip == '0.0.0.0':
        mreq = struct.pack("=4sl", socket.inet_aton(multicast_grp_ip), socket.INADDR_ANY)
    else:
        mreq = struct.pack("=4s4s", \
            socket.inet_aton(multicast_grp_ip), socket.inet_aton(recv_nic_ip))
    receiver.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    # Receive the mssage
    buf, senderaddr = receiver.recvfrom(1024)
    msg = buf.decode()

    # Release resources
    receiver.close()
    return msg 

def wait_forever_for_server_address():
    # wait forever to receive the server ip/port multicast
    print("Waiting to receive server IP address and Port")
    buf=multicast_recv("0.0.0.0",MC_GROUP_ADDRESS,MC_PORT)
    msg=json.loads(buf)
    ip=msg[0]['ip']
    port=msg[1]['port']
    return "http://" + ip + ':' + str(port)

if __name__=='__main__':
    if len(sys.argv) < 2:
        help_and_exit(sys.argv[0])

    cmd = sys.argv[1]
    if cmd == 'send':
        # send or advertise mode
        if len(sys.argv) < 4:
            help_and_exit(sys.argv[0])
        server_ip = sys.argv[2]
        server_port = int(sys.argv[3])
        msg = json.dumps([{"ip":server_ip},{"port":server_port}])

        while True:
            multicast_send(server_ip, msg.encode())
            time.sleep(10)
    elif cmd == 'recv':
        # receive mode
        while True:
            msg = multicast_recv(RECV_NIC_IP, MC_GROUP_ADDRESS, MC_PORT)
            print(msg)
