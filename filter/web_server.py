import BaseHTTPServer, cgi
from filter import Filter

# Changes to the hosts file don't seem to be recoginzed right away. Maybe we
# should act as a proxy server instead of frequently modifying the hosts file.
# Twisted looks promising.
# Make multithreaded so it can handle multiple connections simultaneously.

def html_dict(d):
  ret = ''
  for k, v in d.iteritems():
    ret += '<b>%s:</b> [%s]<br>\n'%(k, v)
  return ret

class Request(object):
  def __init__(self):
    pass

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
  def do_GET(self):
    global flter
    
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    
    host = self.headers['Host']
    req = {}
    req['Path'] = self.path
    ret = ''
    ret += html_dict(req)
    if self.command == 'POST':
      form = cgi.FieldStorage(fp=self.rfile,
        headers=self.headers,
        environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type']})
      post = {}
      for field in form.keys():
        post[field] = form[field].value
      ret += '<br><br>POST data:<br>\n'
      ret += html_dict(post)
    ret += """<form method="post" action="%s">
    Name: <input type="text" name="name"><br>
    <input type="submit" name="submit" value="Submit">
    </form>"""%self.path
    
    self.wfile.write(ret)
    self.wfile.close()
    return
    
    print 'request'
    if host == '127.0.0.1':
      print 'unblock'
      ret = flter.undeter_requested()
      if ret == True:
        self.wfile.write("refresh the page")
      else:
        self.wfile.write(ret)
    else:
      print 'deter'
      self.wfile.write(flter.website_requested(host))
    
    self.wfile.close()

  do_POST = do_GET

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
