import BaseHTTPServer, hashlib, Image, ImageDraw, ImageFont, cStringIO, random, string, os
from string import Template

# def render() is called to display the deterrent.
# def undeter_requested() is called to see if the user can continue to the website requested. 

# Abstract class. Implemented by following deterrent classes.
class AbstractDeterrent(object):
  def render(self, request):
    raise NotImplementedError
  
  def undeter_requested(self, request):
    raise NotImplementedError

# Completely blocks a website with no other action available
class DenyDeterrent(AbstractDeterrent):
  def render(self, request):
    return 'This website is completely blocked and no further action can be taken!'

  def undeter_requested(self, request):
    return self.render(request)

# A random string is generated and turned into an image.
# The user then has to type the string correctly to get
# to the requested website.
class StrChrDeterrent(AbstractDeterrent):
  def render(self, request):
    # Create a random 32 character string consisting of upper and lower case letters
    s = ''.join([random.choice(string.lowercase+string.uppercase) for x in xrange(32)])
    # Find the hash of the string
    s_hash = hashlib.sha1(s).hexdigest()
    # Load the font for the image
    font=ImageFont.load_default()
    # Find the width and height for the image
    text_width, text_height = font.getsize(s)
    # Create a blank image
    img = Image.new("RGB", (text_width,text_height), "#FFFFFF")
    # Draw the text on the image
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), s, fill=(0, 0, 0))
    # Save the image in the webroot
    filename = s_hash+".JPEG"
    file_path = os.path.join(request.webroot, filename)
    img.save(file_path, "JPEG")
    # HTML to send to the browser, showing the string image and text field
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
      # Get the string the user typed in
      userText = request.post['strChar_text']
      computerText = request.post['HashShouldBe']
      # Find its hash
      rp_hash = hashlib.sha1(userText).hexdigest()
      # If the hashes are the same, continue to website
      if rp_hash == computerText:
        return True
    # If not, deny and user must type in a new string of characters
    content = """
    ACCESS DENIED! <br>
    You have typed an incorrect string.<br>
    <a href="http://%s%s">Retry</a>
    """%(request.target_host, request.path)
    return content

# A role model image and quote is displayed in order to get
# the user back on track with their projects
class RoleModelDeterrent(AbstractDeterrent):
  def __init__(self, role_model):
    self.role_model = role_model
  
  def render(self, request):
    # Parse the image path for just the image's file name
    image_path = os.path.basename(self.role_model.picture_path)
    # Pick a random quote from the quote list
    image_quotes = self.role_model.quotes
    rand_num = random.randrange(0,len(image_quotes))
    selected_quote = image_quotes[rand_num]
    # Display the role model and random quote in the browser
    # and see if the user still wants to continue
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
    # Continue to the website
    userAns = request.post['continuePage']
    if userAns == 'Yes':
      return True
    else:
      # User decided to refrain from the website
      content = """
      You've made a wise decision. I admire your restraint.
      """
      return content

# The user is presented with a text box asking them to
# explain how the website helps them with their project.
class BenefitDeterrent(AbstractDeterrent):
  def render(self, request):
    # HTML to display the text box so the user can explain
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
    # If the text box had at least one character, continue to the website.
    if userText is not None and len(userText) > 0:
      return True
    else:
      # The user did not type anything, access denied, must retry
      content = """
      ACCESS DENIED! <br>
      Your reason is not good enough.<br>
      <a href="http://%s%s">Retry</a>
      """%(request.target_host, request.path)
      return content

# Handles which deterrent needs to be called.
class DeterrentFactory(object):
  type_deterrent_map = [DenyDeterrent, StrChrDeterrent, RoleModelDeterrent,
    BenefitDeterrent]

  # Returns the type of deterrent.
  @staticmethod
  def deterrent_for_type(det_type, *args):
    klass = DeterrentFactory.type_deterrent_map[det_type]
    return klass(*args)
