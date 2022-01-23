#  coding: utf-8 
import socketserver
import os

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
        self.requestType = self.requestParts[0][2:] #Slicing cuts out "b'"

        #TODO move based on profs response to question
        try:
            self.url = self.requestParts[1] 
        except IndexError:
            #Handle empty request
            print("Received empty request")
            return
                
           
        self.__pickStatus()
        return       
       

    def __pickStatus(self):
       #TODO add check so that files are only served from ./www and deeper
        if (self.requestType == "GET"):
            if (self.url == "/"):
                #Handle index requests
                #self.file = "www{}index.html".format(self.url)
                self.path = os.path.join("www", "index.html")
            elif (self.url[-1] == "/"):
                #self.file = os.path.join("www", self.url, "index.html") #TODO make self.file cross platform
                self.path = "./www{}/index.html".format(self.url)
            else:
                #Handle non index requests
                #self.file = os.path.join(os.getcwd(), "www", self.url) #TODO make self.file cross platform
                self.path = "./www{}".format(self.url)
    
            self.__handleGet()
            return       
        else:
            #Send 405 cannont handle error
            self.__handle405()
            return


    def __handleGet(self):
        try:
            with open(self.path, "r") as file: #Can raise FileNotFoundError or NotADirectoryError
                self.body = file.read() #Can raise IsADirectoryError
            self.__handle200()
            return
        except FileNotFoundError:
            self.__handle404()
            return
        except NotADirectoryError:
            try:
                self.location301 = "http://127.0.0.1:8080" + self.path[5:-1] 
                self.path = self.path[:-1] #Removes extra '/' from file path
                open(self.path, "r")
                self.__handle301()
                return
            except (FileNotFoundError, NotADirectoryError, NotADirectoryError) as exception:
                self.__handle404()
                return
        except IsADirectoryError:
            try:
                self.location301 = "http://127.0.0.1:8080" + self.path[5:] + "/" 
                self.path = "./www/{}/index.html".format(self.url) #Gets path of index for directory entered without ending '/'
                open(self.path, "r")
                self.__handle301()
                return
            except (FileNotFoundError, NotADirectoryError, NotADirectoryError) as exception:
                self.__handle404()
                return



    def __handle200(self):
        self.fileSize = os.path.getsize(self.path) #TODO fix, test with curl -v
        #https://stackoverflow.com/a/541408 #TODO cite properly
        self.fileExt = os.path.splitext(self.path)[1][1:]
        self.statusCode = "200 Ok"
        self.__sendData()
        return

    def __handle301(self):
        self.statusCode = "301 Moved Permanently"
        self.fileExt = "html"
        self.body = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
        "http://www.w3.org/TR/html4/strict.dtd">
        <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
                <title>Error response</title>
            </head>
            <body>
                <h1>Error response</h1>
                <p>Error code: 301</p>
                <p>Message: Moved Permanently.</p>
                <p>Error code explanation: HTTPStatus.MOVED_PERMANENTLY - The document you have requested has moved to <a href="{0}">{0}</a></p>
            </body>
        </html>'''.format(self.location301)
        self.fileSize = len(self.body)
        self.__sendData()
        return
    

    def __handle404(self):
        self.statusCode = "404 Not Found"
        self.fileExt = "html"
        self.body = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
        "http://www.w3.org/TR/html4/strict.dtd">
        <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
                <title>Error response</title>
            </head>
            <body>
                <h1>Error response</h1>
                <p>Error code: 404</p>
                <p>Message: File not found.</p>
                <p>Error code explanation: HTTPStatus.NOT_FOUND - Nothing matches the given URI.</p>
            </body>
        </html>'''
        self.fileSize = len(self.body)
        self.__sendData()
        return

    def __handle405(self):
        self.statusCode = "405 Method Not Allowed"
        self.fileExt = "html"
        self.body = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
        "http://www.w3.org/TR/html4/strict.dtd">
        <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
                <title>Error response</title>
            </head>
            <body>
                <h1>Error response</h1>
                <p>Error code: 405</p>
                <p>Message: Method Not Allowed ({0}).</p>
                <p>Error code explanation: HTTPStatus.METHOD_NOT_ALLOWED - You are not authorized to use the ({0}) method.</p>
            </body>
        </html>
        '''.format(self.requestType)
        self.fileSize = len(self.body)
        self.__sendData()
        return

    def __sendData(self):
        #TODO add date
        if ("405" in self.statusCode):
            self.payload = "HTTP/1.1 {}\r\nServer: Ryan's Server\r\nContent-type: text/{}; charset=utf-8\r\nContent-Length: {}\r\nAllow: GET\r\n\r\n{}\r\n".format(self.statusCode, self.fileExt, self.fileSize, self.body)
        elif ("301" in self.statusCode):
            self.payload = "HTTP/1.1 {}\r\nServer: Ryan's Server\r\nContent-type: text/{}; charset=utf-8\r\nContent-Length: {}\r\nLocation: {}\r\n\r\n{}\r\n".format(self.statusCode, self.fileExt, self.fileSize, self.location301, self.body)
        else:
            self.payload = "HTTP/1.1 {}\r\nServer: Ryan's Server\r\nContent-type: text/{}; charset=utf-8\r\nContent-Length: {}\r\n\r\n{}\r\n".format(self.statusCode, self.fileExt, self.fileSize, self.body)
        #print(self.payload)
        self.request.sendall(bytearray(self.payload,'utf-8'))
        return

    

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


# GET /pub/WWW/TheProject.html HTTP/1.1 (example GET)



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

'''
404 trial run:


student@cmput404:~$ curl -v http://0.0.0.0:8000/meme
*   Trying 0.0.0.0...
* TCP_NODELAY set
* Connected to 0.0.0.0 (127.0.0.1) port 8000 (#0)
> GET /meme HTTP/1.1
> Host: 0.0.0.0:8000
> User-Agent: curl/7.61.0
> Accept: */*
> 
* HTTP 1.0, assume close after body
< HTTP/1.0 404 File not found
< Server: SimpleHTTP/0.6 Python/3.6.7
< Date: Fri, 21 Jan 2022 01:00:04 GMT
< Connection: close
< Content-Type: text/html;charset=utf-8
< Content-Length: 469
< 
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
        "http://www.w3.org/TR/html4/strict.dtd">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
        <title>Error response</title>
    </head>
    <body>
        <h1>Error response</h1>
        <p>Error code: 404</p>
        <p>Message: File not found.</p>
        <p>Error code explanation: HTTPStatus.NOT_FOUND - Nothing matches the given URI.</p>
    </body>
</html>



'''


'''
Got a request of: b'GET /deep/deep.css HTTP/1.1\r\nHost: 0.0.0.0:8080\r\nUser-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0\r\nAccept: text/css,*/*;q=0.1\r\nAccept-Language: en-CA,en-US;q=0.7,en;q=0.3\r\nAccept-Encoding: gzip, deflate\r\nReferer: http://0.0.0.0:8080/deep/index.html\r\nConnection: keep-alive'

Got a request of: b''

----------------------------------------
Exception happened during processing of request from ('127.0.0.1', 43464)
Traceback (most recent call last):
  File "/usr/lib/python3.6/socketserver.py", line 317, in _handle_request_noblock
    self.process_request(request, client_address)
  File "/usr/lib/python3.6/socketserver.py", line 348, in process_request
    self.finish_request(request, client_address)
  File "/usr/lib/python3.6/socketserver.py", line 361, in finish_request
    self.RequestHandlerClass(request, client_address, self)
  File "/usr/lib/python3.6/socketserver.py", line 721, in __init__
    self.handle()
  File "server.py", line 39, in handle
    self.url = self.requestParts[1]
IndexError: list index out of range
----------------------------------------





'''
'''
curl -X DELETE http://localhost:8000  
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
        "http://www.w3.org/TR/html4/strict.dtd">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
        <title>Error response</title>
    </head>
    <body>
        <h1>Error response</h1>
        <p>Error code: 501</p>
        <p>Message: Unsupported method ('DELETE').</p>
        <p>Error code explanation: HTTPStatus.NOT_IMPLEMENTED - Server does not support this operation.</p>
    </body>
</html>
'''

'''
301 example

 curl -v http://google.com 
* Rebuilt URL to: http://google.com/
*   Trying 142.250.217.78...
* TCP_NODELAY set
* Connected to google.com (142.250.217.78) port 80 (#0)
> GET / HTTP/1.1
> Host: google.com
> User-Agent: curl/7.61.0
> Accept: */*
> 
< HTTP/1.1 301 Moved Permanently
< Location: http://www.google.com/
< Content-Type: text/html; charset=UTF-8
< Date: Sun, 23 Jan 2022 01:12:42 GMT
< Expires: Tue, 22 Feb 2022 01:12:42 GMT
< Cache-Control: public, max-age=2592000
< Server: gws
< Content-Length: 219
< X-XSS-Protection: 0
< X-Frame-Options: SAMEORIGIN
< 
<HTML><HEAD><meta http-equiv="content-type" content="text/html;charset=utf-8">
<TITLE>301 Moved</TITLE></HEAD><BODY>
<H1>301 Moved</H1>
The document has moved
<A HREF="http://www.google.com/">here</A>.
</BODY></HTML>
'''