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
    filename = os.path.join(os.getcwd(), s_hash+".JPEG")
    img.save(filename, "JPEG")
    content="""
    Type the following string in order to continue: <br>
    %s<br>
    <img src="%s" height="%s" width="%s" />
    <br><br>
    <form action="request.path" method="post">
    <input type="text" name="strChar_text" size="50" maxlength="100">
    <input type="hidden" name="HashShouldBe" value="%s"><br><br>
    <input type="submit" value="Submit" />
    </form>
    """%(s,filename, text_height, text_width, s_hash)
    return content

  def undeter_requested(self, request):
    try:
      userText = request.post['strChar_text']
      computerText = request.post['HashShouldBe']
      rp_hash = hashlib.sha1(userText).hexdigest()
      if rp_hash == computerText:
        content = """
        Click <a href="%s">here</a> to continue...
        """%(self.url)
        return content
      else:
        content = """
        ACCESS DENIED! <br>
        You have typed an incorrect string.
        """
        return content
    except:
      return "Error: wrong parameters given."

class RoleModelDeterrent(AbstractDeterrent):
  def __init__(self, role_model):
    self.role_model = role_model
  
  def render(self, request):
    return 'Not yet implemented'
  
  def undeter_requested(self, request):
    try:
      return 'Not yet implemented'
    except:
      return "Error: wrong parameters given."

class BenefitDeterrent(AbstractDeterrent):
  def render(self, request):
    content="""
    <form action="request.path" method="post">
    How does this website benefit your project? <br>
    <textarea name="benefit_text" rows=7 cols=46></textarea> <br>
    <input type="submit" value="Submit" />
    </form>
    """
    return content
  
  def undeter_requested(self, request):
    try:
      userText = read_params['benefit_text']
      if len(userText) > 0:
        content = """
        Click <a href="%s">here</a> to continue...
        """%(self.url)
        return content
      else:
        content = """
        ACCESS DENIED! <br>
        Your reason is not good enough.
        """
        return content
    except:
      return "Error: wrong parameters given."

class DeterrentFactory(object):
  type_deterrent_map = [DenyDeterrent, StrChrDeterrent, RoleModelDeterrent,
    BenefitDeterrent]

  @staticmethod
  def deterrent_for_type(det_type, *args):
    klass = DeterrentFactory.type_deterrent_map[det_type]
    return klass(*args)
