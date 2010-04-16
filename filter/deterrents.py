import BaseHTTPServer, hashlib

class Deterrent:
  def __init__(self):
    self.type
    self.role_models
    

class RoleModel:
  def __init__(self):
    self.name
    self.quotes
    self.image_paths

# Check out string.Template if you'd like to use templates for your HTML.
def get_deterrent():
  s = "Hello, world!"
  return '%s: %s'%(s, hashlib.sha1(s).hexdigest())

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
  def do_GET(self):
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    self.wfile.write(get_deterrent())
    self.wfile.close()

print 'starting'
addr = ('127.0.0.1', 8080)
httpd = BaseHTTPServer.HTTPServer(addr, RequestHandler)
print 'forever'
httpd.serve_forever()
