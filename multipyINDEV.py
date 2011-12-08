#This version of multipy does not work!

def create_udp_socket(port, blocking=1):
    #Creates a UDP socket. Takes 1 or 2 arguments (port, blocking=0)
    socket = socket(AF_INET, SOCK_DGRAM)
    socket.bind(('', port))
    socket.setblocking(blocking)
    return socket
