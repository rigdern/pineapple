class Website(object):
  def __init__(address, rule):
    self.address = address
    self.rule = rule
    self.blocked = False

class AlwaysBlockRule:
  def is_blocking(self):
    return True

class BlockSchedulingRule:
  def is_blocking(self):
    current_hour = datetime.datetime.now().hour
    return current_hour not in self.blocked_hours

class TimeToleranceRule:
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


class Filter(object):
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
