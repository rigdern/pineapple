import BaseHTTPServer
from filter import Filter

# Changes to the hosts file don't seem to be recoginzed right away. Maybe we
# should act as a proxy server instead of frequently modifying the hosts file.
# Twisted looks promising.
# Make multithreaded so it can handle multiple connections simultaneously.

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
  def do_GET(self):
    host = self.headers['Host']
    
    print 'request'
    if host == '127.0.0.1':
      print 'unblock'
      self.handle_unblock_request()
    else:
      print 'deter'
      self.handle_deterrent()

  def handle_unblock_request(self):
    global flter
    
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    
    url = self.path[1:]
    # XXX This should only be possible for certain URL's. In fact, it might be
    # appropriate to disabe this. The server itself will handle the unblocking
    # when appropriate.
    flter.unblock(url)
    print 'Unblocked [%s]'%url
    
    self.wfile.write('unblocked [%s]'%url)
    self.wfile.close()
  
  def handle_deterrent(self):
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    
    self.wfile.write('show deterrent')
    self.wfile.close()

  do_POST = do_GET

flter = Filter('configs/sampler')
addr = ('127.0.0.1', 80)
httpd = BaseHTTPServer.HTTPServer(addr, RequestHandler)
try:
  print 'serving'
  httpd.serve_forever()
finally:
  flter.shut_down()
print 'done'
