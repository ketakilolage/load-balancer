import unittest
import os
import pexpect
import requests
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

LB_BINARY = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "load_balancer"))

class MockServerRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        '''
        We override the do_GET method of the BaseHTTPRequestHandler.
        This method is called when a client sends a GET request .
        '''
        self.send_response(200)
        self.end_headers()
        self.wfile.write('Mock backend server started!')

class TestCanProxyHTTPRequestToBackend(unittest.TestCase):
    def runTest(self):
        # We create a backend server which will handle HTTP requests
        httpd = HTTPServer(('127.0.0.1', 8888), MockServerRequestHandler)
        thread = Thread(target=httpd.serve_forever)
        thread.daemon = True
        thread.start()
        
        print("here", __file__)
        # We instantiate the load balancer and point it towards the backend server
        lbalancer = pexpect.spawn(LB_BINARY, ['8000', '127.0.0.1', '8888']) 
        lbalancer.expect('Started load balancer on port 8000!')         # it waits for this output from the spawned process
        
        # try sending requests to the balancer
        try:
            response = requests.get("http://127.0.0.1:8000")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.text, 'Mock backend server started!')

            response = requests.get("http://127.0.0.1:8000")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.text, 'Mock backend server started!')

        finally:
            lbalancer.kill()
            httpd.shutdown()
unittest.main()