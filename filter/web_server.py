import BaseHTTPServer

# Changes to the hosts file don't seem to be recoginzed right away. Maybe we
# should act as a proxy server instead of frequently modifying the hosts file.
# Twisted looks promising.
# Make multithreaded so it can handle multiple connections simultaneously.

# XXX Path to hosts file should depend on the operating system
def read_hosts():
  hosts = {}
  for line in open('/etc/hosts').readlines():
    if '#' in line:
      line = line[:line.index('#')]
    parts = line.split()
    if len(parts) == 2:
      addrs = hosts.setdefault(parts[1], set())
      addrs.add(parts[0])
  return hosts

def write_hosts(hosts):
  fp = open('/etc/hosts', 'w')
  for name, addrs in hosts.iteritems():
    for addr in addrs:
      fp.write('%s\t%s\n'%(addr, name))
  fp.close()

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
  def do_GET(self):
    global hosts
    
    host = self.headers['Host']
    
    if host == '127.0.0.1':
      self.send_response(200)
      self.send_header("Content-type", "text/html")
      self.end_headers()
      url = self.path[1:]
      del hosts[url]
      write_hosts(hosts)
      print 'Unblocked [%s]'%url
      self.wfile.write('unblocked [%s]'%url)
      self.wfile.close()
    else:
      self.send_response(200)
      self.send_header("Content-type", "text/html")
      self.end_headers()
      url = 'http://' + host + self.path
      # XXX The HTML shouldn't be hardcoded in here. It should be in a separate
      #     file. If we need to use too much Python to generate the HTML, perhaps
      #     we should look into a templating system.
      content = """
<html>
<head>
  <title>Blocked</title>
  <script language="JavaScript">
  <!--
    function unblock(host)
    {
      var req = new XMLHttpRequest();
      req.open("GET", "http://127.0.0.1/" + host, true);
      req.onreadystatechange = function (aEvt) {
        if (req.readyState == 4)
          location.reload(true);
      }
      req.send(null);
    }
  -->
  </script>
</head>
<body>
Denied! You cannot access %s.
<br><br>
Click <a href="javascript:unblock('%s')">here</a> to access it.<br><br>
</body>
</html>
"""
      self.wfile.write(content%(url, host))
      self.wfile.close()

  do_POST = do_GET

# XXX We should have a better way to deal with the hosts file.
orig_hosts = read_hosts()
hosts = read_hosts()

print 'starting'
addr = ('127.0.0.1', 80)
httpd = BaseHTTPServer.HTTPServer(addr, RequestHandler)
print 'forever'
try:
  httpd.serve_forever()
finally:
  write_hosts(orig_hosts)
print 'done'