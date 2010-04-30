"""
filter.py

Defines a system for hooking web requests and connecting the request to the
appropriate rule and deterrent.
"""

import pickle
import os
import shutil
from deterrents import DeterrentFactory
from rules import RuleFactory

DET_TYPE_DENY = 0
DET_TYPE_TYPE = 1
DET_TYPE_ROLES = 2
DET_TYPE_EXPLAIN = 3
ROLE_FILE_NAME = "myRoles"


def find_if(pred, seq):
    """Returns the first element of *seq* for which the predicate *pred*
    returns true. Returns None otherwise."""
    for x in seq:
        if pred(x):
            return x
    return None


class RoleModel(object):
    """Represents a role model to be displayed by the filter. Includes a name,
    picture, and quotes."""
    def __init__(self, params):
        self.name = params['Name']
        self.quotes = params['QuotesList']
        self.picture_path = params['ImagePath']

# XXX Path to hosts file for Windows shouldn't assume it'll be no the C drive.
class HostsFile(object):
    """An abstraction to represent the hosts file. Functions such as *add* and
    *remove* change the in-memory object. No changes are made to disk until
    *save* is called. The hosts file can be returned to its original state
    by calling *restore*."""
    UNIX_PATH = '/etc/hosts'
    WINDOWS_PATH = 'C:\\Windows\\System32\\Drivers\\etc\\hosts'

    def __init__(self):
        if hasattr(os, 'uname'):
            self.path = HostsFile.UNIX_PATH
        else:
            self.path = HostsFile.WINDOWS_PATH
        self._back_up_hosts_file(self.path)
        self.orig_hosts_data = open(self.path).read()
        self.hosts = self._read_hosts(self.path)

    def add(self, host_name, addr):
        """Add an entry to associate *host_name* with *addr*."""
        addrs = self.hosts.setdefault(host_name, set())
        addrs.add(addr)

    def remove(self, host_name):
        """Remove all entries involving *host_name*."""
        if host_name in self.hosts:
            del self.hosts[host_name]
            return True
        return False

    def save(self):
        self._write_hosts(self.hosts, self.path)
        os.system("ipconfig /flushdns")

    def restore(self):
        """Return the hosts file to the state that it was in when this HostsFile
        object was created."""
        fp = open(self.path, 'w')
        fp.write(self.orig_hosts_data)
        fp.close()

    def _read_hosts(self, path):
        hosts = {}
        for line in open(path).readlines():
            if '#' in line:
                line = line[:line.index('#')]
            parts = line.split()
            if len(parts) == 2:
                addrs = hosts.setdefault(parts[1], set())
                addrs.add(parts[0])
        return hosts

    def _write_hosts(self, hosts, path):
        fp = open(path, 'w')
        for name, addrs in hosts.iteritems():
            for addr in addrs:
                fp.write('%s\t%s\n' % (addr, name))
        fp.close()

    def _back_up_hosts_file(self, path):
        """Create a back up of the hosts file called hosts-bkup in the same
        directory as the hosts file."""
        bkup_path = os.path.join(os.path.dirname(self.path), 'hosts-bkup')
        if not os.path.exists(bkup_path):
            shutil.copy(path, bkup_path)


class Filter(object):
    """Represents a web filter. Provides an interface for configuring which
    websites should be filtered and by what rules and deterrents the filtering
    should happen. The filter is expected to be initialized from a project
    configuration file created by the Configuration Utility."""
    def __init__(self, config_path):
        self.hosts = HostsFile()
        self.load_role_models(ROLE_FILE_NAME)
        self.load_rules(config_path)

    def load_role_models(self, path):
        """Load the role models file into memory."""
        self.role_models = {}
        if os.path.exists(path):
            for model in pickle.load(open(path)):
                self.role_models[model['Name']] = RoleModel(model)

    def load_rules(self, config_path):
        """Read the rules and deterrents into memory from the project
        configuration file stored at *config_path*."""
        self.rules = {}
        for raw_rule in pickle.load(open(config_path)):
            address = raw_rule['url']
            deterrent_type = int(raw_rule['Deterrents']['Method'])
            if deterrent_type == DET_TYPE_ROLES:
                deterrent = DeterrentFactory.deterrent_for_type(deterrent_type,
                  self.role_models[raw_rule['Deterrents']['RoleModelName']])
            else:
                deterrent = DeterrentFactory.deterrent_for_type(deterrent_type)
            self.rules[address] = RuleFactory.rule_for_dict(self, address, deterrent, raw_rule['BlockConfig'])

    def website_requested(self, request):
        """Returns the HTML that should be rendered to the user when *request*
        has been made by the user."""
        try:
            return self._html_wrap(self.rules[request.target_host].deterrent.render(request))
        except KeyError:
            return "Host not supposed to be used with filter: %s" % request.target_host

    def undeter_requested(self, request):
        """Either returns True or some HTML. If True is returned, it means
        that the website associated with *request* has been unblocked and
        that the user should be redirected to the page they requested. If HTML
        is returned, this means that the website is still blocked and the HTML
        should be rendered to the user instead."""
        try:
            address = request.target_host
            rule = self.rules[address]
            ret = rule.deterrent.undeter_requested(request)
            if ret == True:
                self.unhook(address)
                rule.undeterred()
                return True
            else:
                return self._html_wrap(ret)
        except KeyError:
            return "Host not supposed to be used with filter: %s" % address

    def start(self):
        """The filter should now be in effect. Let the rules begin!"""
        [rule.enable() for rule in self.rules.itervalues()]

    def shut_down(self):
        """Stop filtering. Inform the rules that they are no longer needed and
        restore the hosts file to its original form."""
        [rule.disable() for rule in self.rules.itervalues()]
        self.hosts.restore()

    def hook(self, address):
        """Begin intercepting requests for *address*."""
        self.hosts.add(address, '127.0.0.1')
        self.hosts.save()

    def unhook(self, address):
        """Stop intercepting requests for *address*."""
        self.hosts.remove(address)
        self.hosts.save()

    def _html_wrap(self, body):
        """The HTML layout that our filter returns to the user. Returns the
        layout with *body* interpolated into the middle of it."""
        title = "Pineapple Web Filter"
        blocked = "BLOCKED!"
        content = """
        <html><head><title>%s</title></head><body>
        <DIV ALIGN=CENTER>
        <h1>%s<br>%s</h1>
        %s
        </div>
        </body></html>
          """
        return '%s' % (content % (title, title, blocked, body))
