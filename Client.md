# Import the library #
First off, import the multipy library

`import multipy`

You can alternatively import just the client base class

`from multipy import Client`

# Wrapping a class #
Multipy uses a base class for both server and client.
An example client class:
```
class BareBonesClient(multipy.Client):
    
    def on_connect(self, cid):
        print("We've connected!")
        
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
# To call instance of client #
```
my_client = BareBonesClient(name = 'client1', port = 0, timeout = 5)

my_client.connect(ip = 'localhost', port = 1200)
```
`my_client.connect()` connects the client to the server