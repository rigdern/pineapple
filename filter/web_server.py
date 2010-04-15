import BaseHTTPServer, urllib2, socket, select

unblocked = set()

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
  def proxy_it(self):
    host = self.headers['Host']
    addr = '98.137.149.56'#socket.gethostbyname_ex(host)
    port = 80
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((addr, port))
    
    req = "%s %s %s\r\n"%(self.command, self.path, self.request_version)
    s.send(req)
    for key, value in self.headers.items():
      header = '%s: %s\r\n'%(key, value)
      s.send(header)
    s.send('\r\n')
    
    read_files = [s, self.rfile]
    write_files = []
    error_files = read_files
    print 'piping...'
    while 1:
      ins, _, errs = select.select(read_files, write_files, error_files, 3.0)
      if not ins and not errs:
        break
      
      for f in errs:
        print 'Exception', f
      
      for in_file in ins:
        if in_file == self.rfile:
          out = s
        else:
          out = self.wfile
        if hasattr(in_file, 'recv'): data = in_file.recv(1024)
        else: data = in_file.read(1024)
        if data:
          if hasattr(out, 'send'): out.send(data)
          else: out.write(data)
        else:
          break
    print 'Connection CLOSED'
    s.close()
    self.wfile.close()
    self.rfile.close()
  
  def proxy_it_good(self):
    host = self.headers['Host']
    addr = '98.137.149.56'#socket.gethostbyname_ex(host)
    port = 80
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((addr, port))
    
    req = "%s %s %s\r\n"%(self.command, self.path, self.request_version)
    s.send(req)
    print req
    for h in self.headers:
      header = '%s: %s\r\n'%(h.title(), self.headers[h])
      s.send(header)
    s.send('\r\n')
    
    while 1:
      r, w, x = select.select([s, self.rfile], [], [s, self.rfile])
      for a in x:
        print 'Exception', a
      if self.rfile in r:
        print 'data from CLIENT'
        data = self.rfile.read(1024)
        if len(data) == 0:
          self.rfile.close()
          self.wfile.close()
          s.close()
          print 'CLOSED via CLIENT'
          break
        print 'GOT IT: [%s]'%data
        s.sendall(data)
      if s in r:
        print 'data from SERVER'
        data = s.recv(1024)
        if len(data) == 0:
          s.close()
          self.rfile.close()
          self.wfile.close()
          print 'CLOSED via SERVER'
          break
        print 'GOT IT: [%s]'%data
        self.wfile.write(data)
    
  def proxy_it2(self):
    host = self.headers['Host']
    addr = '98.137.149.56'#socket.gethostbyname_ex(host)
    port = 80
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((addr, port))
    
    req = "%s %s %s\r\n"%(self.command, self.path, self.request_version)
    s.send(req)
    print req
    for h in self.headers:
      continue
      print 'HEADER: [%s: %s]'%(string.capwords(h, '-'), self.headers[h])
      s.send('%s: %s\r\n'%(string.capwords(h, '-'), self.headers[h]))
    s.send('\r\n')
    print 'receiving...'
    buf = ''
    while 1:
      data = s.recv(1024)
      if len(data) == 0: break
      buf += data
    print 'got: [%s]'%buf
    s.close()
    print 'sending to client'
    self.send_response(200)
    self.wfile.write(buf)
    self.wfile.close()
  
  def do_GET(self):
    if self.headers['Host'] == '127.0.0.1':
      self.send_response(200)
      self.send_header("Content-type", "text/html")
      self.end_headers()
      url = self.path[1:]
      self.wfile.write('unblocked [%s]'%url)
      unblocked.add(url)
    else:
      self.proxy_it()
      return
      self.send_response(200)
      self.send_header("Content-type", "text/html")
      self.end_headers()
      url = 'http://' + self.headers['Host'] + self.path
      self.wfile.write('<a href="%s">%s</a>'%(url, url))
      print self.path
      #print 'HOST --', self.headers['Host']
      print 'HOST'
      print self.headers
      print '-'*20
      print 'DATA'
      #print self.rfile.closed
      print 'here they come!'
      print 'line: [%s]'%(self.rfile.read(int(self.headers['Content-Length'])))
      print
      print '-'*20
      print

  do_POST = do_GET

print 'starting'
addr = ('127.0.0.1', 80)
httpd = BaseHTTPServer.HTTPServer(addr, RequestHandler)
print 'forever'
httpd.serve_forever()
print 'done'