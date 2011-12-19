import multipy
	
client = multipy.client()
client.connect(ip='localhost', port=1020)

while 1:
	received_data = client.update()
	packet_size = client.send('keep alive')
	
'''The function update() will force the client to check for new data
the client will detect new clients, and remove old ones in this way
The function send(_data) will send a datatype to the host (server) defined on connect(ip, port)

update() will return any received valid packet
send() will return the size of the sent packet in bytes
'''	