import pickle, datetime, time
from threading import Timer

# Should be shared with configuration tool.
DET_TYPE_DENY = 0
DET_TYPE_TYPE = 1
DET_TYPE_ROLES = 2
ROLE_FILE_NAME="myRoles"

def find_if(pred, seq):
  for x in seq:
    if pred(x):
      return x
  return None

class RoleModel(object):
  def __init__(self, params):
    self.name = params['Name']
    self.quotes = params['QuotesList']
    self.picture_path = params['ImagePath']

class Deterrent(object):
  def __init__(self, det_type, role_model=None):
    self.type = det_type
    self.role_model = role_model

class Website(object):
  def __init__(self, address, rule, deterrent):
    self.address = address
    self.rule = rule
    self.deterrent = deterrent
    self.blocked = False
#{'url': 'deny.com', 'BlockConfig': {'Method': 0}, 'BlackWhiteList': 1}
#{'url': 'break.com', 'BlockConfig': {'Method': 1, 'BreakLength': '10'}, 'BlackWhiteList': 1}
#{'url': 'block-schedule.com', 'BlockConfig': {'AllowedTime': ['0', '1', '2', '3', '4', '8', '9'], 'Method': 2}, 'BlackWhiteList': 1}

class AbstractRule(object):
  def __init__(self, flter, address, deterrent, params):
    self.filter = flter
    self.address = address
    self.deterrent = deterrent
  
  def enable(self):
    """Called when the rule will begin taking effect. Initialize the state."""
    pass
  
  def disable(self):
    """Called when the rule will no longer be considered. Clean up."""
    pass
  
  def undeterred(self):
    """Called when the user has chosen to bypass the deterrent. Prepare for
    re-enabling the deterrent."""
    pass

class DeterOnceRule(AbstractRule):
  """Deter the user until he accepts the deterrent. Afterwards, allow access
  to the website."""
  def enable(self):
    self.filter.hook(self.address)

class TimeToleranceRule(AbstractRule):
  """When a user accepts the deterrent, allow uninterrupted access to the
  website for x minutes. After x minutes have elapsed, re-enable the
  deterrent."""
  def __init__(self, flter, address, deterrent, params):
    AbstractRule.__init__(self, flter, address, deterrent, params)
    self.allowed_duration = int(params['BreakLength'])*60
    self.block_duration = int(params['TimeBetweenBreaks'])*60
    self.timer = None
  
  def enable(self):
    self.filter.hook(self.address)
  
  def disable(self):
    if self.timer:
      self.timer.cancel()
      self.timer = None
  
  def undeterred(self):
    """Re-enable the deterrent after *allowed_duration* minutes."""
    self.timer = Timer(self.allowed_duration, self._hook_address, [])
    self.timer.start()
  
  def _hook_address(self):
    self.timer = None
    self.filter.hook(self.address)

class BlockSchedulingRule(AbstractRule):
  """Allow uninterrupted access to the website during the allowed hours. For
  all other hours, deter the user once in each hour."""
  def __init__(self, flter, address, deterrent, params):
    AbstractRule.__init__(self, flter, address, deterrent, params)
    self.allowed_hours = [int(x) for x in params['AllowedTime']]
  
  def enable(self):
    if self._current_hour() in self.allowed_hours:
      self._establish_timer(self._next_deterred_hour(), self._hook_address)
    else:
      self.filter.hook(self.address)
      self._establish_timer(self._next_allowed_hour(), self._unhook_address)
  
  def disable(self):
    self._cancel_timer()
  
  def undeterred(self):
    self._cancel_timer()
    self._establish_timer(self._next_deterred_hour(), self._hook_address)
  
  def _hook_address(self):
    self.filter.hook(self.address)
    self._establish_timer(self._next_allowed_hour(), self._unhook_address)
  
  def _unhook_address(self):
    self.filter.unhook(self.address)
    self._establish_timer(self._next_deterred_hour(), self._hook_address)
  
  def _establish_timer(self, end_time, callback):
    # XXX What if now is more in the future than next_time by the time we get
    # to the subtraction code? Race condition.
    if end_time is not None:
      self.timer = Timer(end_time - time.time(), callback)
  
  def _cancel_timer(self):
    if self.timer:
      self.timer.cancel()
      self.timer = None
  
  def _current_hour(self):
    return datetime.datetime.now().hour
  
  def _next_hour(self, allowed):
    # If we're looking for an allowed hour, make sure at least one exists.
    # If we're looking for a deterred hour, make sure at least one exists.
    if allowed and len(self.allowed_hours) == 0 \
      or (not allowed and len(self.allowed_hours) == 24):
      return None
    
    if allowed:
      pred = lambda hour: hour in self.allowed_hours
    else:
      pred = lambda hour: hour not in self.allowed_hours
    
    base = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    # When's the next hour TODAY?
    hour = find_if(pred, range(self._current_hour()+1, 24))
    if hour is None:
      # Nothing today. When's the next hour TOMORROW?
      base += datetime.timedelta(days=1)
      hour = find_if(pred, range(0, self._current_hour()+1))
    
    return time.mktime(base.replace(hour=hour).timetuple())
  
  def _next_allowed_hour(self):
    return self._next_hour(True)
  
  def _next_deterred_hour(self):
    return self._next_hour(False)

class RuleFactory:
  method_rule_map = [DeterOnceRule, TimeToleranceRule, BlockSchedulingRule]
  
  @staticmethod
  def rule_for_dict(flter, address, deterrent, params):
    klass = RuleFactory.method_rule_map[params['Method']]
    return klass(flter, address, deterrent, params)

# XXX Path to hosts file should depend on the operating system
class HostsFile(object):
  UNIX_PATH = '/etc/hosts'
  def __init__(self):
    self.path = HostsFile.UNIX_PATH
    self.orig_hosts_data = open(self.path).read()
    self.hosts = self._read_hosts(self.path)
  
  def add(self, host_name, addr):
    addrs = self.hosts.setdefault(host_name, set())
    addrs.add(addr)
  
  def remove(self, host_name):
    if host_name in self.hosts:
      del self.hosts[host_name]
      return True
    return False
  
  def save(self):
    self._write_hosts(self.hosts, self.path)
  
  def restore(self):
    fp = open('/etc/hosts', 'w')
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
        fp.write('%s\t%s\n'%(addr, name))
    fp.close()

class Filter(object):
  def __init__(self, config_path):
    self.hosts = HostsFile()
    self.load_role_models(ROLE_FILE_NAME)
    self.load_rules(config_path)
  
  def load_role_models(self, path):
    self.role_models = {}
    for model in pickle.load(open(path)):
      self.role_models[model['Name']] = RoleModel(model)
  
  def load_rules(self, config_path):
    self.rules = {}
    for raw_rule in pickle.load(open(config_path)):
      address = raw_rule['url']
      deterrent_type = int(raw_rule['Deterrents']['Method'])
      if deterrent_type == DET_TYPE_ROLES:
        role_model = self.role_models[raw_rule['Deterrents']['RoleModelName']]
        deterrent = Deterrent(deterrent_type, role_model)
      else:
        deterrent = Deterrent(deterrent_type)
      self.rules[address] = RuleFactory.rule_for_dict(self, address, deterrent, raw_rule['BlockConfig'])
  
  def website_requested(self, address, request):
    try:
      return self.rules[address].deterrent.render(request)
    except KeyError:
      return "Host not supposed to be used with filter: %s"%address
  
  def undeter_requested(self, address, request):
    try:
      rule = self.rules[address]
      ret = rule.deterrent.undeter_requested(request)
      if ret == True:
        self.unhook(address)
        rule.undeterred()
        return True
      else:
        return ret
    except KeyError:
      return "Host not supposed to be used with filter: %s"%address
  
  def start(self):
    [rule.enable() for rule in self.rules.itervalues()]
  
  def shut_down(self):
    [rule.disable() for rule in self.rules.itervalues()]
    self.hosts.restore()
  
  def hook(self, address):
    self.hosts.add(address, '127.0.0.1')
    self.hosts.save()
  
  def unblock(self, address):
    self.hosts.remove(address)
    self.hosts.save()

if __name__ == '__main__':
  f = Filter("configs/sampler")
  dets = ['Deny', 'Type a Long String', 'Role Model']
  for url, w in f.websites.iteritems():
    print url, w.rule.__class__.__name__
    if w.rule.__class__ == DeterOnceRule:
      print '\tAlways block'
    elif w.rule.__class__ == TimeToleranceRule:
      print '\tUse time:', w.rule.allowed_duration
      print '\tBreak time:', w.rule.block_duration
    elif w.rule.__class__ == BlockSchedulingRule:
      print '\tAllowed hours:', w.rule.allowed_hours
    else:
      print '\tUnknown rule:', w.rule.__class__
    print '\tDeterrent:', dets[w.deterrent.type],
    if w.deterrent.type == DET_TYPE_ROLES:
      print '(%s)'%w.deterrent.role_model.name
    else:
      print

  print '-'*40
  print 'ROLE MODELS'
  for rm in f.role_models.itervalues():
    print '%s (%s)'%(rm.name, rm.picture_path)
    print '\t' + '\n\t'.join(rm.quotes)
