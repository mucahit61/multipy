import multipy
	
client = multipy.client(port=2800)
client.connect(ip='localhost', port=1060)

while 1:
	client.update()
	client.send('asdfg')
	
'''The function update() will force the client to check for new data
the client will detect new clients, and remove old ones in this way
The function send(_data) will send a datatype to the host (server) defined on connect(ip, port)
'''	