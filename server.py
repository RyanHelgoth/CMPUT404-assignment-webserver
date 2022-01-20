#  coding: utf-8 
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

# https://docs.python.org/3/library/socketserver.html 
class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        self.requestParts = str(self.data).split()
        self.requestType = self.requestParts[0]
        self.url = self.requestParts[1]
        #Might need to get host

        if (self.requestType == "GET"):
            #Send data based on url
            with open("index.html", "r") as indexHTML:
                self.indexHTMLString = indexHTML.read()
            
            self.fileSize = len(self.indexHTMLString)
            #TODO add date
            self.header = "HTTP/1.0 200 OK\r\nServer: Ryan's Server\r\nContent-type: text/html; charset=utf-8\r\nContent-Length: {}".format(self.fileSize)
            self.request.sendall(bytearray(self.indexHTMLString,'utf-8'))
        else:
            #Send 405 cannont handle error
            pass

        #self.request.sendall(bytearray("OK",'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
    print("Sever started")

    server.handle()




'''
Incoming GET:
> GET / HTTP/1.1
> Host: 0.0.0.0:8000
> User-Agent: curl/7.61.0
> Accept: */*
> 

Response to GET:
< HTTP/1.0 200 OK
< Server: SimpleHTTP/0.6 Python/3.6.7
< Date: Thu, 20 Jan 2022 19:57:31 GMT
< Content-type: text/html; charset=utf-8
< Content-Length: 2125
< 
*BODY* (serve "/" aka "./www" files)




'''

'''
Trial run:
student@cmput404:~$ curl http://0.0.0.0:8080/
curl: (52) Empty reply from server

student@cmput404:~/Assignments/CMPUT404-assignment-webserver$ python3 server.py
Got a request of: b'GET / HTTP/1.1\r\nHost: 0.0.0.0:8080\r\nUser-Agent: curl/7.61.0\r\nAccept: */*'


'''