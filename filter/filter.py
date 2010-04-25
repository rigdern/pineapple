import pickle

# Should be shared with configuration tool.
DET_TYPE_DENY = 0
DET_TYPE_TYPE = 1
DET_TYPE_ROLES = 2
ROLE_FILE_NAME="myRoles"

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
  def __init__(self, params):
    pass
  
  def is_blocking(self, params):
    raise NotImplementedError
  
  def website_visited(self):
    pass

class AlwaysBlockRule(AbstractRule):
  def is_blocking(self):
    return True

class TimeToleranceRule(AbstractRule):
  def __init__(self, params):
    self.allowed_duration = int(params['BreakLength'])*60
    self.block_duration = int(params['TimeBetweenBreaks'])*60
  
  def is_blocking(self):
    now = time.time()
    if self.block_start is None:
      return False
    elif self.block_start <= now <= self.block_end:
      return True
    else:
      return False
  
  def website_visited(self):
    now = time.time()
    if self.block_start is None:
      self.block_start = now + self.allowed_duration
      self.block_end = self.block_start + self.block_duration
    elif now > self.block_end:
      self.block_start = self.block_end = None

class BlockSchedulingRule(AbstractRule):
  def __init__(self, params):
    self.allowed_hours = [int(x) for x in params['AllowedTime']]
  
  def is_blocking(self):
    current_hour = datetime.datetime.now().hour
    return current_hour in self.allowed_hours

class RuleFactory:
  method_rule_map = [AlwaysBlockRule, TimeToleranceRule, BlockSchedulingRule]
  
  @staticmethod
  def rule_for_dict(params):
    klass = RuleFactory.method_rule_map[params['Method']]
    return klass(params)

class Filter(object):
  def __init__(self, config_path):
    self.load_role_models(ROLE_FILE_NAME)
    self.load_websites(config_path)
  
  def load_role_models(self, path):
    self.role_models = {}
    for model in pickle.load(open(path)):
      self.role_models[model['Name']] = RoleModel(model)
  
  def load_websites(self, config_path):
    self.websites = {}
    for raw_website in pickle.load(open(config_path)):
      address = raw_website['url']
      rule = RuleFactory.rule_for_dict(raw_website['BlockConfig'])
      deterrent_type = int(raw_website['Deterrents']['Method'])
      if deterrent_type == DET_TYPE_ROLES:
        role_model = self.role_models[raw_website['Deterrents']['RoleModelName']]
        deterrent = Deterrent(deterrent_type, role_model)
      else:
        deterrent = Deterrent(deterrent_type)
      self.websites[address] = Website(address, rule, deterrent)
    
  def website_visited(self, url):
    website = self.websites[url]
    website.rule.website_visited()
  
  def is_blocked(self, url):
    website = self.websites[url]
    if website.blocked != website.rule.is_blocking():
      if website.blocked:
        self._unblock(website)
      else:
        self._block(website)
    return website.blocked
  
  def _block(self, website):
    website.blocked = True
  
  def _unblock(self, url):
    website.blocked = False

f = Filter("configs/sampler")
dets = ['Deny', 'Type a Long String', 'Role Model']
for url, w in f.websites.iteritems():
  print url, w.rule.__class__.__name__
  if w.rule.__class__ == AlwaysBlockRule:
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
