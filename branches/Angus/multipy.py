from socket import socket, AF_INET, SOCK_DGRAM
from random import randint
from math import ceil
from classes import states, entity, packer
from time import time
				
class server:
	'''main server class
	'''
	
	def __init__(self, port = 1000, timeout = 3, limit = 4, ping = 60):
		'''creates a server instance
		:param port: the port for the server to communicate on (handler)
		:param timeout: the time in seconds before client timeout
		:param limit: the maximum clients that can connect
		:param ping: the interval in seconds between client ping
		'''
		
		self.handler_port = port
		self.manager_port = port + 1
		self.timeout = timeout
		self.limit = limit
		self.ping = ping
		self.client_dic = { }
		self.ip_dic = { }
		self.ban_list = []
		
		self.handler = socket(AF_INET, SOCK_DGRAM)
		self.manager = socket(AF_INET, SOCK_DGRAM)
		self.handler.bind(('localhost', self.handler_port))
		self.manager.bind(('localhost', self.manager_port))
		self.handler.setblocking(0)
		self.manager.setblocking(0)	 
		print('server initialised')

	def add_client(self, name, ip):	 
		'''register new client
		:param name: the name of the client to store
		:param ip: the address [ip, port] of the client to store
		'''
		
		def connection_id():
			'''generates a random id for connection
			'''
			limit = ceil(float(len(self.client_dic)) / 10) * 10
			id = randint(0, limit)
			if id in self.client_dic.keys():
				id = connection_id(self)
			return(id)
		
		id = connection_id()
		timeout = [time(), 0]
		state = states.states['new_connection']
		data = [state, self.manager_port, id]			
		
		self.handler.sendto(packer.pack(data), ip)
		self.ip_dic[ip] = entity(name, id, ip, timeout)
		self.client_dic[id] = self.ip_dic[ip]
		print("{} connected".format(id))
		
	def remove_client(self, id, ip):
		'''force client removal
		:param id: the universal id of the client to be removed
		:param ip: the address [ip, port] of the client to remove
		'''
		
		state = states.states['remove_connection']
		data = [state, id]
		
		self.client_dic.pop(id)
		self.ip_dic.pop(ip)				
		
		for ip, entity_id in self.ip_dic.items():
			if entity_id == id:
				continue
			try:
				self.handler.sendto(packer.pack(data), ip)
			except Exception as Error:
				print(Error)
			
	def listen(self):
		'''listens new connections to the server
		'''
				
		try:
			packet, ip = self.handler.recvfrom(1024)
		except:
			return
		
		try:		
			state, name = packer.unpack(packet)
		except:
			#bad packet
			pass
		
		if len(self.client_dic) == self.limit:
			data = [state]
			self.handler.sendto(packer.pack(data), ip)
		
		if ip in self.ban_list:
			return
		
		if not ip in self.ip_dic.keys():
			self.add_client(name, ip)

			
	def route(self):
		'''routes client data to clients
		'''
		
		try:
			packet, ip = self.manager.recvfrom(1024)
		except:
			return
		
		try:
			state, id, data, rpc = packer.unpack(packet)
		except:
			#invalid packet
			return
		print(packer.unpack(packet))		
		if not id in self.client_dic.keys():
			print('not in')
			return  
				
		for entity_ip, entity_id in self.ip_dic.items():
			if entity_id == id:
				continue
			data = ([state, id, data, rpc])
			self.handler.sendto(packet, entity_ip)
			
		entity = self.client_dic[id]	
		entity.timeout[0] = time()
		
	def admin(self):
		'''runs the server protocols
		'''
		
		remove_clients = []
		
		for ip, entity in self.ip_dic.items():
			last_received, count = entity.timeout	
			difference = time() - last_received
			entity.timeout[1] = difference			
			
			if difference > self.timeout:
				print('client {0} timed out after {1} seconds'.format(entity.id, difference))
				remove_clients.append([entity.id, ip])
				
		for id, ip in remove_clients:
			self.remove_client(id, ip)
			
	def start(self):	
		
		'''similar to socketserver's server_forever()'''	
		while 1:
			self.listen()
			self.route()
			self.admin()
			
			
class client:
	'''main client class'''
	
	def __init__(self, name = 'client', port = 2745, timeout = 3):
		'''initialises the client
		:param name: the name of the client
		:param port: the port for the client to communicate over
		:param timeout: the time in seconds before the client aborts connection
		'''
				
		self.local = ('localhost', port)
		self.name = name
		self.id = name
		self.timeout = timeout
		
		self.connected = False
		self.id_to_name = {}
		self.name_to_id = {}
		
		self.tunnel = socket(AF_INET, SOCK_DGRAM)
		self.tunnel.bind(self.local)
		self.tunnel.setblocking(0)	
		print('client initialised')
	
	def connect(self, ip = 'localhost', port = 1012):
		'''connect to the server, and store connection
		:param ip: the ip address of the host
		:param port: the port of the host
		'''
		
		if self.connected:
			return
		
		self.server = (ip, port)
		state = states.states['new_connection']
		name = self.name
		data = ([state, name])
		self.tunnel.sendto(packer.pack(data), self.server)
		
		#TODO: [COMPLETED]: force timeout of connection
		start_time = time()
		
		while not self.connected:
			current_time = time()
			if (current_time - start_time) > self.timeout:
				break 
			try:
				packet, ip = self.tunnel.recvfrom(1024)
			except:
				continue
			
			self.connected = True
			state, port, id = packer.unpack(packet)	
			self.server = (self.server[0], port)
			self.id = id
			print('client connected: {}'.format(self.server))
			return
		print('client could not reach host: {}'.format(self.server))
		
	def update(self):
		'''checks for new data and updates core data
		returns any received data
		'''
		
		try:
			packet, ip = self.tunnel.recvfrom(1024)
		except:
			return
		
		try:
			state, id, data, rpc = packer.unpack(packet)
		except:
			#invalid packet
			return
			
		if state == states.states['remove_connection']:
			if id in self.id_to_name.keys():
				self.name_to_id.pop(self.id_to_name[id])
				self.id_to_name.pop(id)
				print('client {} disconnected'.format(id))
			return
		
		if not id in self.id_to_name.keys():
			self.id_to_name[id] = None
			print('client {} connected'.format(id))
			
		return data
		
		#TODO: [COMPLETED]: return received data to called
		
	def send(self, _data):
		'''send a datatype to the server
		:param _data: the data to be compressed and sent to the host
		returns the size of the packet
		'''
		
		if not object:
			return
		_state = states.states['established_connection']
		_id = self.id
		_rpc = None
		data = ([_state, _id, _data, _rpc])		
		packet_size = self.tunnel.sendto(packer.pack(data), self.server)
		return packet_size