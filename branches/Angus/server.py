import multipy

myserver = multipy.server(port=1060, timeout=3, limit=4)

myserver.start()

'''The function start() will simulate a server_forever() function
the server will:
>Listen for new connections
>forward existing client data
>remove timed out connections'''
