import BaseHTTPServer, SimpleHTTPServer, cgi, os, sys
from filter import Filter

# Changes to the hosts file don't seem to be recoginzed right away. Maybe we
# should act as a proxy server instead of frequently modifying the hosts file.
# Twisted looks promising.
# Make multithreaded so it can handle multiple connections simultaneously.

WEBROOT = "webroot"

class Request(object):
  def __init__(self, webroot=None, path=None, post_data=None, target_host=None):
    self.webroot = webroot
    self.path = path
    self.post = post_data
    self.target_host = target_host

class RequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
  def do_HEAD(self):
    os.chdir(WEBROOT)
    try:
      SimpleHTTPServer.SimpleHTTPRequestHandler.do_HEAD(self)
    finally:
      os.chdir('..')
  
  def handle_request(self):
    global flter
    
    host = self.headers['Host']
    request = Request(WEBROOT, self.path, self.post_data())
    
    if host == '127.0.0.1':
      if self.command == 'GET' and self.path != '/':
        # Serve a static file.
        os.chdir('webroot')
        try:
          SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
        finally:
          os.chdir('..')
      else:
        try:
          request.target_host = request.post['host']
          ret = flter.undeter_requested(request)
        except KeyError:
          self.send_ok("Malformed request: 'host' form parameter missing")
          return
        if ret == True:
          redirect_url = "http://%s%s"%(request.target_host, self.path)
          self.send_redirect(redirect_url)
        else:
          self.send_ok(ret)
    else:
      request.target_host = host
      self.send_ok(flter.website_requested(request))
  
  def post_data(self):
    post_data = {}
    if self.command == 'POST' and 'Content-Type' in self.headers:
      form = cgi.FieldStorage(fp=self.rfile,
        headers=self.headers,
        environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type']})
      for field in form.keys():
        post_data[field] = form[field].value
    return post_data
  
  def send_ok(self, content):
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    self.wfile.write(content)
    self.wfile.close()
  
  def send_redirect(self, redirect_url):
    self.send_response(301)
    self.send_header("Location", redirect_url)
    self.end_headers()

  do_POST = do_GET = handle_request

def main():
  global flter
  
  if len(sys.argv) != 2:
    print "Usage: python %s <path-to-project>"%sys.argv[0]
    sys.exit()
  
  flter = Filter(sys.argv[1])
  flter.start()
  if not os.path.exists(WEBROOT):
    old = os.umask(0002)
    try:
      os.makedirs(WEBROOT)
    finally:
      os.umask(old)
  addr = ('127.0.0.1', 80)
  httpd = BaseHTTPServer.HTTPServer(addr, RequestHandler)
  try:
    print 'serving'
    httpd.serve_forever()
  except KeyboardInterrupt:
    print 'goodbye'
  finally:
    flter.shut_down()
    for file_name in os.listdir(WEBROOT):
      if file_name.endswith(".JPEG"):
        os.remove(os.path.join(WEBROOT, file_name))
  print 'done'

if __name__ == '__main__':
  main()
