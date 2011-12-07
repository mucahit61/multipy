from socket import socket, AF_INET, SOCK_DGRAM
from rencode import dumps, loads
from random import randint
from math import ceil

class entity:
	def _init__(self, name, id, ip, timeout):
		self.name = name
		self.id = id
		self.ip = ip
		self.timeout = timeout
		self.latency = [0, 100, 100]
		
class packer:
	def __init__(self):
		pass
		
	def pack(self, data):
		'''packs data for socket'''
		return dumps(data)
		
	def unpack(self, data):
		'''unpacks data from socket'''
		return loads(data)
		
class server:
	def __init__(self, port = 1000, timeout = 120, limit = 4, ping = 60, package = False, size = 6):
		'''creates a server instance'''
		self.states = {
			'new_connection':'#1',
			'remove_connection':'#2',
			'limit_connection':'#3',
			'ping_connection':'#4',
			'established_connection':'#5',
		}	
		
		self.port = port
		self.timeout = timeout
		self.limit = limit
		self.ping = ping
		self.package = [package, size]
		self.client_dic = { }
		self.ip_dic = { }
		self.ban_list = []
		
		self.handler = socket(AF_INET, SOCK_DGRAM)
		self.manager = socket(AF_INET, SOCK_DGRAM)
		self.handler.bind(('localhost', self.port))
		self.manager.bind(('localhost', self.port+1))
		self.handler.setblocking(0)
		self.manager.setblocking(0)	
		print('server initialised')
		
	def connection_id(self):
		'''generates a random id for connection'''
		limit = ceil(float(len(self.client_dic)) / 10) * 10
		id = randint(0, limit)
		if str(id) in self.client_dic.keys():
			id = connection_id(self)
		return(str(id))
	
	def add_connection(self, name, ip):	
		'''adds the new connection to the server'''
		id = connection_id()
		timeout = self.timeout
		state = self.states['new_connection']
		data = [state, self.port, id]
		
		self.handler.sendto(packer.pack(data), ip)
		self.ip_dic[ip] = self.client_dic[id] = entity(name, id, ip, timeout)
		print(id, "connected")
		
	def remove_connection(self, id, ip):
		'''forces connection removal'''
		state = self.states['remove_connection']
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
		'''listens new connections to the server'''
		try:
			packet, ip = self.handler.recvfrom(1024)
		except:
			return
			
		state, name = packer.unpack(packet)
		
		if len(self.client_dic) == self.limit:
			data = [state]
			self.handler.sendto(packer.pack(data), ip)
		
		if ip in self.ban_list:
			return
		
		if not ip in self.ip_dic.keys():
			add_connection(self, name, ip)
		
	def manage(self):
		'''runs the server protocols'''
		
		try:
			packet, ip = self.manager.recvfrom(1024)
		except:
			return
		
		try:
			state, id, data, rpc = packer.unpack(packet)
		except:
			#invalid packet
			return
			
		if not id in self.client_dic.keys():
			return	
			
		for entity_ip, entity_id in self.ip_dic.items():
			if entity_id == id:
				continue
			data = ([state, id, data, rpc])
			self.handler.sendto(packer.pack(data), entity_ip)
			
	def start(self):		
		while 1:
			self.listen()
			self.manage()
class client:
	def __init__(self, ip = 'localhost', port = 1000, name = 'client', frequency = 15, local_port = 2000, timout = 120):
		pass