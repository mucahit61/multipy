from rencode import dumps, loads

class states:
	'''states used by the server / client
	'''
	def __init__(self):
		pass
	
	states = {
	'new_connection':0,
	'remove_connection':1,
	'limit_connection':2,
	'ping_connection':3,
	'established_connection':4,
			}   
	
class entity:
	'''a client entity
	'''
	def __init__(self, name, id, ip, timeout):
		self.name = name
		self.id = id
		self.ip = ip
		self.timeout = timeout #0 is the time last received, #1 is the difference
		self.latency = [0, 100, 100]
			
class packer:
	'''how data is packed / unpacked
	'''
	def __init__(self):
		pass
	
	def pack(data):
		'''packs data for socket
		'''
		return dumps(data)
			
	def unpack(data):
		'''unpacks data from socket
		'''
		return loads(data)