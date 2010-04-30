"""
web_server.py

Usage: python web_server.py <path-to-project>

When run, starts the filter. Takes a path to a project configuration file
as a command line parameter. When appropriate, serves static files from
WEBROOT. In other situations, forwards intercepted requests to the filter.
"""

import BaseHTTPServer
import SimpleHTTPServer
import cgi
import os
import sys
from filter import Filter

# Changes to the hosts file don't seem to be recoginzed right away. Maybe we
# should act as a proxy server instead of frequently modifying the hosts file.
# Twisted looks promising.
# Make multithreaded so it can handle multiple connections simultaneously.

WEBROOT = "webroot"


class Request(object):
    """Represents a webrequest made by the user. Includes information that
    the filter needs to know about the request.
    *webroot* - The location of all static files our web server can serve.
    *path* - The path portion of the URL that the user requested.
    *post* - A dictionary representing the form data the user has submitted.
    *target_host* - The hostname that the user is trying to reach."""
    def __init__(self, webroot=None, path=None, post_data=None,
        target_host=None):
        self.webroot = webroot
        self.path = path
        self.post = post_data
        self.target_host = target_host


class RequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """The core of the web server. An instance is created for each web
    request."""
    def do_HEAD(self):
        """Handle an HTTP HEAD request. SimpleHTTPRequestHandler only serves
        files from the current directory. We want to serve files only from
        WEBROOT so we make WEBROOT the current directory and then let
        SimpleHTTPRequestHandler do its job."""
        os.chdir(WEBROOT)
        try:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_HEAD(self)
        finally:
            os.chdir('..')

    def handle_request(self):
        """Handles the majority of web requests from the user. It has a few
        general modes. The mode depends on the hostname and the request type:
        1. 127.0.0.1, GET
           Serves static files from WEBROOT. Used for serving the "captcha"
           images and the role model pictures.
        2. 127.0.0.1, POST
           The user wants undeter the website stored in the *host* POST
           parameter. See if they've cleared the deterrent.
        3. not 127.0.0.1, GET or POST
           The user is trying to access a blocked webpage. Show them the
           appropriate deterrent."""
        global flter

        host = self.headers['Host']
        request = Request(WEBROOT, self.path, self.post_data())

        if host == '127.0.0.1':
            if self.command == 'GET' and self.path != '/':
                # Mode 1: Serve a static file.
                os.chdir('webroot')
                try:
                    SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
                finally:
                    os.chdir('..')
            else:
                # Mode 2: See if the user has properly passed the deterrent.
                try:
                    request.target_host = request.post['host']
                    ret = flter.undeter_requested(request)
                except KeyError:
                    self.send_ok("Malformed request: 'host' form parameter missing")
                    return
                if ret == True:
                    redirect_url = "http://%s%s" % (request.target_host, self.path)
                    self.send_redirect(redirect_url)
                else:
                    self.send_ok(ret)
        else:
            # Mode 3: The user is trying to access a blocked page. Deter them.
            request.target_host = host
            self.send_ok(flter.website_requested(request))

    def post_data(self):
        """Returns the raw form data as a python dictionary. The keys are the
        form element names and the values are the user-submitted form
        values."""
        post_data = {}
        if self.command == 'POST' and 'Content-Type' in self.headers:
            form = cgi.FieldStorage(fp=self.rfile,
              headers=self.headers,
              environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type']})
            for field in form.keys():
                post_data[field] = form[field].value
        return post_data

    def send_ok(self, content):
        """Returns *content* to the browser."""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(content)
        self.wfile.close()

    def send_redirect(self, redirect_url):
        """Redirects the browser to *redirect_url*."""
        self.send_response(301)
        self.send_header("Location", redirect_url)
        self.end_headers()
    
    # Set GET and POST requests to be handled by the handle_request function.
    do_POST = do_GET = handle_request


def main():
    """Get everything started. Initialize the filter from the configuration
    file specified by the first command line argument. Start the web server
    for the filter."""
    global flter

    if len(sys.argv) != 2:
        print "Usage: python %s <path-to-project>" % sys.argv[0]
        sys.exit()

    flter = Filter(sys.argv[1])
    flter.start()
    # If the WEBROOT directory doesn't exist, create it and make sure
    # the user can write to it.
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
            # Delete the "captchas."
            if file_name.endswith(".JPEG"):
                os.remove(os.path.join(WEBROOT, file_name))
    print 'done'

if __name__ == '__main__':
    main()
