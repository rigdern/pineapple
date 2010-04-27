import BaseHTTPServer, hashlib, Image, ImageDraw, ImageFont, cStringIO, random, string, os
from string import Template

class AbstractDeterrent(object):
  def render(self, request):
    raise NotImplementedError
  
  def undeter_requested(self, request):
    raise NotImplementedError

class DenyDeterrent(AbstractDeterrent):
  def render(self, request):
    return 'This website is completely blocked and no further action can be taken!'

  def undeter_requested(self, request):
    return self.render(request)

class StrChrDeterrent(AbstractDeterrent):
  def render(self, request):
    s = ''.join([random.choice(string.lowercase+string.uppercase+string.digits) for x in xrange(50)])
    s_hash = hashlib.sha1(s).hexdigest()
    font=ImageFont.load_default()
    text_width, text_height = font.getsize(s)
    img = Image.new("RGB", (text_width,text_height), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), s, fill=(0, 0, 0))
    filename = s_hash+".JPEG"
    file_path = os.path.join(request.webroot, filename)
    img.save(file_path, "JPEG")
    # XXX urlencode request.path? Use HTML entities?
    content="""
    Type the following string in order to continue: <br>
    <img src="http://127.0.0.1/%s" />
    <br><br>
    <form action="http://127.0.0.1%s" method="post">
    <input type="text" name="strChar_text" size="50" maxlength="100">
    <input type="hidden" name="HashShouldBe" value="%s">
    <input type="hidden" name="host" value="%s"><br><br>
    <input type="submit" value="Submit" />
    </form>
    """%(filename, request.path, s_hash, request.target_host)
    return content

  def undeter_requested(self, request):
    if 'strChar_text' in request.post and 'HashShouldBe' in request.post:
      userText = request.post['strChar_text']
      computerText = request.post['HashShouldBe']
      rp_hash = hashlib.sha1(userText).hexdigest()
      if rp_hash == computerText:
        return True
    
    content = """
    ACCESS DENIED! <br>
    You have typed an incorrect string.<br>
    <a href="http://%s%s">Retry</a>
    """%(request.target_host, request.path)
    return content

class RoleModelDeterrent(AbstractDeterrent):
  def __init__(self, role_model):
    self.role_model = role_model
  
  def render(self, request):
    image_path = os.path.basename(self.role_model.picture_path)
    image_quotes = self.role_model.quotes
    rand_num = random.randrange(0,len(image_quotes))
    selected_quote = image_quotes[rand_num]
    content="""
    <img src="http://127.0.0.1/rolemodels/%s" /><br>
    <i>%s</i><br>
    &mdash; %s
    <br><br>
    Still want to continue? <br>
    <form action="http://127.0.0.1%s" method="post">
    <input type="hidden" name="host" value="%s">
    <input type="submit" name="continuePage" value="Yes" />
    <input type="submit" name="continuePage" value="No" />
    </form>
    """%(image_path, selected_quote, self.role_model.name, request.path, request.target_host)
    return content
  
  def undeter_requested(self, request):
    userAns = request.post['continuePage']
    if userAns == 'Yes':
      return True
    else:
      content = """
      You've made a wise decision. I admire your restraint.
      """
      return content

class BenefitDeterrent(AbstractDeterrent):
  def render(self, request):
    content="""
    <form action="http://127.0.0.1%s" method="post">
    How does this website benefit your project? <br>
    <textarea name="benefit_text" rows=7 cols=46></textarea> <br>
    <input type="hidden" name="host" value="%s">
    <input type="submit" value="Submit" />
    </form>
    """%(request.path, request.target_host)
    return content
  
  def undeter_requested(self, request):
    userText = request.post.get('benefit_text', None)
    if userText is not None and len(userText) > 0:
      return True
    else:
      content = """
      ACCESS DENIED! <br>
      Your reason is not good enough.<br>
      <a href="http://%s%s">Retry</a>
      """%(request.target_host, request.path)
      return content

class DeterrentFactory(object):
  type_deterrent_map = [DenyDeterrent, StrChrDeterrent, RoleModelDeterrent,
    BenefitDeterrent]

  @staticmethod
  def deterrent_for_type(det_type, *args):
    klass = DeterrentFactory.type_deterrent_map[det_type]
    return klass(*args)
