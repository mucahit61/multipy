# Import the library #
First off, import the multipy library

`import multipy`

You can alternatively import just the server base class

`from multipy import Server`

# Wrapping a class #
Multipy uses a base class for both server and client.
An example server class:
```
class BareBonesServer(multipy.Server):
    
    def on_receive(self, data):
        # data is the uncompressed packet
        pass
    
    def on_client_connect(self, cid):
        # cid is the id of the connected client
        pass
    
    def on_client_disconnect(self, cid):
        # cid is the id of the disconnected client
        pass
    
    def on_send(self, data):
        # data is the uncompressed packet
        pass
```
If it doesn't exist, the on\_receive callback would forward the data received to each client but the sending client by default. In this example, it does nothing.
An example on\_receive callback:
```
try:
	state, cid, data, rpc = data
except ValueError:
	print("packet could not be unpacked")
	
self.send(data, [ip for ip, entity in self.ip_dic.items() if entity.cid != cid])	
```
# To call a server instance #
First, call an instance of the server:
```
my_server = BareBonesServer(port = 1200, timeout = 3, limit = 4, ping = 60)
```
You can change how the server runs depending on if it is enclosed in a frame-by-frame environment, such as PyGame or Blender Game Engine:
The forever flag runs in a while loop:
```
my_server.update(forever=True)
```
Therefore setting it to false / leaving it updates for one frame
```
my_server.update() # forever=False
```