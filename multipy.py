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
		self.paused = False
		
		handler = ('localhost', self.handler_port)
		manager = ('localhost', self.manager_port)
		
		self.handler = socket(AF_INET, SOCK_DGRAM)
		self.manager = socket(AF_INET, SOCK_DGRAM)
		self.handler.bind(handler)
		self.manager.bind(manager)
		self.handler.setblocking(0)
		self.manager.setblocking(0)	 
		
		initialised = [
		'server listener initialised: {}'.format(handler),
		'server manager initialised: {}'.format(manager),			
					]
		for alert in initialised:
			print(alert)
		
		biggest_alert = max([len(alert) for alert in initialised])
		print(''.join(['-' for i in range(biggest_alert)]))
		
	def add_client(self, name, ip):	 
		'''register new client
		:param name: the name of the client to store
		:param ip: the address [ip, port] of the client to store
		'''
		
		def connection_cid():
			'''generates a random cid for connection
			'''
			limit = ceil(float(len(self.client_dic)) / 10) * 10
			cid = randint(0, limit)
			if cid in self.client_dic.keys():
				cid = connection_cid(self)
			return(cid)
		
		cid = connection_cid()
		timeout = [time(), 0]
		state = states.states['new_connection']
		data = [state, self.manager_port, cid]			
		
		self.handler.sendto(packer.pack(data), ip)
		self.ip_dic[ip] = entity(name, cid, ip, timeout)
		self.client_dic[cid] = self.ip_dic[ip]
		
		print("{} connected".format(cid))
		
	def remove_client(self, cid, ip):
		'''force client removal
		:param cid: the universal cid of the client to be removed
		:param ip: the address [ip, port] of the client to remove
		'''
		
		state = states.states['remove_connection']
		data = [state, cid]
		
		self.client_dic.pop(cid)
		self.ip_dic.pop(ip)				
		
		for ip, entity_cid in self.ip_dic.items():
			if entity_cid == cid:
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

			
	def manage(self):
		'''interprets client data to clients
		'''
		
		try:
			packet, ip = self.manager.recvfrom(1024)
		except:
			return
		
		try:
			state, cid, data, rpc = packer.unpack(packet)
		except:
			#invalid packet
			return
		
		if not cid in self.client_dic.keys():
			#unregistered client
			return  
				
		# To maintain efficiency, client functions share the data from one port
		# The forwarding is not executed if the server is paused
		# But listens for resume connection calls	
		if self.paused:
			return
		
		# Forward data to other clients
		for ip, entity in self.ip_dic.items():
			if entity.cid == cid:
				continue
			
			data = ([state, cid, data, rpc])
			self.handler.sendto(packet, ip)
		
		# Update entity timouts	
		entity = self.client_dic[cid]	
		entity.timeout = [time(), 0]
		
	def admin(self):
		'''runs the server protocols
		'''
		
		remove_clients = []
		
		for ip, entity in self.ip_dic.items():
			last_received, count = entity.timeout	
			difference = time() - last_received
			entity.timeout[1] = difference			
			
			if difference > self.timeout:
				print('{0} timed out after {1} seconds'.format(entity.cid, difference))
				remove_clients.append([entity.cid, ip])
				
		for cid, ip in remove_clients:
			self.remove_client(cid, ip)
			
	def start(self):
		'''similar to socketserver's server_forever()'''	
		while 1:
			self.manage()
			
			if self.paused:
				continue
			# Update server processes as usual
			self.listen()
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
		self.cid = name
		self.timeout = timeout
		
		self.connected = False
		self.cid_to_name = {}
		self.name_to_cid = {}
		
		self.tunnel = socket(AF_INET, SOCK_DGRAM)
		self.tunnel.bind(self.local)
		self.tunnel.setblocking(0)	
		
		alert = 'client initialised: {}'.format(self.local)
		
		print(alert)
		
		print(''.join(['-' for i in range(len(alert))]))
	
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
			state, port, cid = packer.unpack(packet)	
			self.server = (self.server[0], port)
			self.cid = cid
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
			state, cid, data, rpc = packer.unpack(packet)
		except:
			#invalid packet
			return
			
		if state == states.states['remove_connection']:
			if cid in self.cid_to_name.keys():
				self.name_to_cid.pop(self.cid_to_name[cid])
				self.cid_to_name.pop(cid)
				print('{} disconnected'.format(cid))
			return
		
		if not cid in self.cid_to_name.keys():
			self.cid_to_name[cid] = None
			print('{} connected'.format(cid))
			
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
		_cid = self.cid
		_rpc = None
		data = ([_state, _cid, _data, _rpc])		
		packet_size = self.tunnel.sendto(packer.pack(data), self.server)
		return packet_size