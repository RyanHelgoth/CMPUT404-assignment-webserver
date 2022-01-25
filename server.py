#  coding: utf-8 
import socketserver
import os
import pathlib 
from pathlib import Path



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
        #TODO find way to replace dot segments in url
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
        if (self.requestType == "GET"):
            if (self.url == "/"):
                #Handle root directory requests
                #self.file = "www{}index.html".format(self.url)
                self.path = os.path.join("www", "index.html")
            elif (self.url[-1] == "/" and not "." in self.url):
                #self.file = os.path.join("www", self.url, "index.html") #TODO make self.file cross platform
                #Handles directory requests and file requests with extra "/"
                self.path = "./www{}index.html".format(self.url)
            else:
                #Handles file requests and directory requests with missing "/"
                #self.file = os.path.join(os.getcwd(), "www", self.url) #TODO make self.file cross platform
                self.path = "./www{}".format(self.url) 
    
            
            
           
             
            self.path = os.path.abspath(self.path) #Returns absolute path without dot segments
            self.path = os.path.relpath(self.path) #Gets relative path
            if (self.url[-1] == "/" and "." in self.url):
                #os.path methods remove trailing "/", so it must be readded to trigger 301
                self.path = self.path + "/"

            

            if (not self.path[:3] == "www"):
                #If path does not start with "www", then it is not in a directory that should be served from
                self.__handle404()
                return
            
            print(self.path) #./www/deep/index.html


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
                print("not dir error")
                self.location301 = "http://127.0.0.1:8080/{}".format(self.path[4:-1])# TODO changes might make this uneeded
                self.path = self.path[:-1] #Removes extra '/' from file path
                open(self.path, "r")
                self.__handle301()
                return
            except (FileNotFoundError, NotADirectoryError, NotADirectoryError) as exception:
                self.__handle404()
                return
        except IsADirectoryError:
            try:
                print("is dir error")
                self.location301 = "http://127.0.0.1:8080/{}/".format(self.path[4:])
                self.path = "{}/index.html".format(self.path) #Gets path of index for directory entered without ending '/'
                print(self.path)
                open(self.path, "r")
                self.__handle301()
                return
            except (FileNotFoundError, NotADirectoryError, NotADirectoryError) as exception:
                self.__handle404()
                return



    def __handle200(self):
        self.fileSize = os.path.getsize(self.path) 
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
        if ("405" in self.statusCode):
            self.payload = "HTTP/1.1 {}\r\nServer: Ryan's Server/1.0 Python/3.6.7\r\nConnection: close\r\nContent-type: text/{}; charset=utf-8\r\nContent-Length: {}\r\nAllow: GET\r\n\r\n{}".format(self.statusCode, self.fileExt, self.fileSize, self.body)
        elif ("301" in self.statusCode):
            self.payload = "HTTP/1.1 {}\r\nServer: Ryan's Server/1.0 Python/3.6.7\r\nConnection: close\r\nContent-type: text/{}; charset=utf-8\r\nContent-Length: {}\r\nLocation: {}\r\n\r\n{}".format(self.statusCode, self.fileExt, self.fileSize, self.location301, self.body)
        else:
            self.payload = "HTTP/1.1 {}\r\nServer: Ryan's Server/1.0 Python/3.6.7\r\nConnection: close\r\nContent-type: text/{}; charset=utf-8\r\nContent-Length: {}\r\n\r\n{}".format(self.statusCode, self.fileExt, self.fileSize, self.body)
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
    print("Sever started")
    server.serve_forever()
    


