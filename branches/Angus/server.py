import multipy

myserver = multipy.server(port=1020, timeout=3, limit=5)
myserver.start()

'''The function start() will simulate a server_forever() function
the server will:
>Listen for new connections
>forward existing client data
>remove timed out connections'''
