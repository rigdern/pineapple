import BaseHTTPServer, cgi
from filter import Filter

# Changes to the hosts file don't seem to be recoginzed right away. Maybe we
# should act as a proxy server instead of frequently modifying the hosts file.
# Twisted looks promising.
# Make multithreaded so it can handle multiple connections simultaneously.

class Request(object):
  def __init__(self, path, post_data):
    self.path = path
    self.post = post_data

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
  def handle_request(self):
    global flter
    
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    
    host = self.headers['Host']
    request = Request(self.path, self.post_data())
    
    if host == '127.0.0.1':
      try:
        ret = flter.undeter_requested(request.post['host'], request)
      except KeyError:
        self.wfile.write("Malformed request")
        self.wfile.close()
        return
      if ret == True:
        self.wfile.write("refresh the page")
      else:
        self.wfile.write(ret)
    else:
      self.wfile.write(flter.website_requested(host, request))
    
    self.wfile.close()
  
  def post_data(self):
    post_data = {}
    if self.command == 'POST' and 'Content-Type' in self.headers:
      form = cgi.FieldStorage(fp=self.rfile,
        headers=self.headers,
        environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type']})
      for field in form.keys():
        post_data[field] = form[field].value
    return post_data

  do_POST = do_GET = handle_request

flter = Filter('configs/sampler')
flter.start()
addr = ('127.0.0.1', 80)
httpd = BaseHTTPServer.HTTPServer(addr, RequestHandler)
try:
  print 'serving'
  httpd.serve_forever()
finally:
  flter.shut_down()
print 'done'
