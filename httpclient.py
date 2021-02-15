#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
from pprint import pprint


# you may use urllib to encode data appropriately
import urllib.parse

#TODO get output to print to std out 

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        host_port = urllib.parse.urlparse(url).port

        if host_port == None:
            host_port = 80
        
        return host_port


    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        response_elements = data.split('\r\n')
        first_line = (response_elements[0]).split(' ')
        code = int(first_line[1])
        print('\n--------------------------------------------START--------------------------------------------------\n')
        print("STATUS CODE:", code)
        return code

    def get_headers(self,data):
        response_elements = data.split('\r\n')
        response_elements.pop(0) #remove the response code
        last = len(response_elements) - 2
        # response_elements.pop()
        headers = response_elements[:last]
        print ('\n'.join(headers))

    def get_body(self, data):
        response_elements = data.split('\r\n')
        last_ind = len(response_elements) - 1
        body = response_elements[last_ind]  #get last element
        print(body)
        print('----------------------------------------------END------------------------------------------------\n')
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""

        #get request params
        host_name = urllib.parse.urlparse(url).hostname
        host_port = self.get_host_port(url)
        url_path = urllib.parse.urlparse(url).path

       
        #when the path is not given use server root
        if not url_path:
            url_path = '/'

        #send http get request

        #format of GET request to send
        request_header = 'GET' + ' ' + url_path + ' ' + 'HTTP/1.1\r\nHost: ' + host_name +'\r\nConnection: close\r\n\r\n'

        get_request = str(request_header)


        self.connect(host_name, host_port)  #open a connection 

        #send request
        self.sendall(get_request)

        #get the response from the request
        response = self.recvall(self.socket)

        self.close()

        code = self.get_code(response)
        self.get_headers(response)
        body = self.get_body(response)
        
        return HTTPResponse(code, body) #returns as http response object 

    def POST(self, url, args=None):
        # print(args)
        code = 500
        body = ""

        #open a connection
        post_host_name = urllib.parse.urlparse(url).hostname
        post_host_port = self.get_host_port(url)
        post_url_path = urllib.parse.urlparse(url).path

        if args != None:
            parameters = urllib.parse.urlencode(args)  #encoding the args
            content_length = len(parameters)
        else:
            content_length = 0
            parameters = None
            
        # format of POST request
        post_header = 'POST' + ' ' + post_url_path + ' ' + 'HTTP/1.1\r\nHost: ' + post_host_name + '\r\nConnection: close\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length:' + str(content_length) + '\r\n\r\n' + str(parameters) + '\r\n\r\n'
        post_header = str(post_header)

        self.connect(post_host_name, post_host_port)

        self.sendall(post_header)

        result = self.recvall(self.socket)


        self.close()


        # get code and body
        code = self.get_code(result)
        self.get_headers(result)
        body = self.get_body(result)

        return HTTPResponse(code, body) #returns as http response object

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
