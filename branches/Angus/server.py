import multipy
import pickle

print(pickle.dumps.__doc__)

myserver = multipy.server(port=1059, timeout=3, limit=4)
print(multipy.server.__init__.__doc__)
myserver.start()

'''The function start() will simulate a server_forever() function
the server will:
>Listen for new connections
>forward existing client data
>remove timed out connections'''
