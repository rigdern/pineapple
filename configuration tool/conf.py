# file: conf.py


from Tkinter import *
import tkFileDialog
import os
import pickle

LIST_TYPE_WHITELIST = 0
LIST_TYPE_BLACKLIST = 1

TIME_TYPE_DENY_ALWAYS = 0
TIME_TYPE_ALLOW_BREAKS = 1
TIME_TYPE_BLOCK_SCHEDULING = 2

DET_TYPE_DENY = 0
DET_TYPE_TYPE = 1
DET_TYPE_ROLES = 2


mySites=[]
rbRadios=[]
picRole=0
lastselection = None
myRolesList=[]

ROLE_FILE_NAME="myRoles"
#roleFile=open(ROLE_FILE_NAME,'w')


def removeSite():
	site=SiteStr.get()
	oldSites=lbSiteList.curselection()
	for i in oldSites:
		lbSiteList.delete(i)
		del mySites[int(i)]
		
def addSite():
	siteconfig = {}
	siteconfig['url'] = SiteStr.get()
	SiteStr.set('')
	siteconfig['BlockConfig'] = {}
	siteconfig['BlackWhiteList'] = intListType.get()
	blocktype = intTimeType.get()
	siteconfig['BlockConfig']['Method'] = blocktype
	if blocktype == TIME_TYPE_ALLOW_BREAKS:
		siteconfig['BlockConfig']['BreakLength']=BreakLengthStr.get()
	if blocktype == TIME_TYPE_BLOCK_SCHEDULING:
		allowed_blocks=liTime.curselection()
		siteconfig['BlockConfig']['AllowedTime'] = []
		for allowed_time in allowed_blocks:
			siteconfig['BlockConfig']['AllowedTime'].append(allowed_time)

	# TODO deterrents
	dettype = intDetType.get()
	siteconfig['Deterrents'] = {}
	siteconfig['Deterrents']['Method'] = dettype
	if dettype == DET_TYPE_ROLES:
		rowindex = lbRoleModels.curselection()
		if len(rowindex) != 1:
			print "error: must select a role model"
			return

		siteconfig['Deterrents']['RoleModelName'] = myRolesList[int(rowindex[0])]['Name']

	print siteconfig

	mySites.append(siteconfig)
	lbSiteList.delete(0,END)
	for item in mySites:
		lbSiteList.insert(END,item['url'])

def openFile():
	global mySites
        infile = tkFileDialog.askopenfile(parent=root,mode='rb',title='Choose a configuration file to open')
	if infile != None:
		mySites = pickle.load(infile)
		if mySites == None or len(mySites) == 0:
			return
		print mySites
		lbSiteList.delete(0, END)
		for k in mySites:
			lbSiteList.insert(END, k['url'])

def saveFile():
	fileName = tkFileDialog.asksaveasfilename(parent=root, title="Save the configuration file as...")
	if len(fileName) > 1:
		outfile = open(fileName, 'wb')
		pickle.dump(mySites, outfile)
		print mySites
		outfile.close()
		
	
def poll():
	global lastselection
	currentselection = lbSiteList.curselection()
	if currentselection != lastselection:
		lastselection = currentselection
		list_selection_changed(currentselection)
	lbSiteList.after(200, poll)

def list_selection_changed(selection):
	if len(selection) < 1:
		return
	BreakLengthStr.set('')
	configobj = mySites[int(selection[0])]
	liTime.select_clear(0, END)
	SiteStr.set(configobj['url'])
	blockmethod = configobj['BlockConfig']['Method']
	rbTimeRadios[blockmethod].select()
	if (blockmethod == TIME_TYPE_ALLOW_BREAKS):
		BreakLengthStr.set(str(configobj['BlockConfig']['BreakLength']))
	elif (blockmethod == TIME_TYPE_BLOCK_SCHEDULING):
		breaks = configobj['BlockConfig']['AllowedTime']
		for allowedtime in breaks:
			liTime.selection_set(allowedtime)

	deterrentmethod = configobj['Deterrents']['Method']
	intDetType.set(deterrentmethod)
	if deterrentmethod == DET_TYPE_ROLES:
		roleName = configobj['Deterrents']['RoleModelName']
		for i in range(0, len(myRolesList)):
			if myRolesList[i]['Name'] == roleName:
				lbRoleModels.selection_set(i)
	lookForEdit(None)
		
def lookForEdit(event):
	return
	prevvalue = SiteStr.get()
	if event != None:
		if not event.char.isalnum() and event.char != '.':
			return
		SiteStr.insert(prevvalue + event.char)

	isadd = 1
	for site in mySites:
		if SiteStr.get() == site['url']:
			bSite.config(text="Edit Site")
			isadd = 0
			break
	if isadd:
		bSite.config(text="Add Site")
		

	return "break"


def loadRoleModel():
	global lbRolePrev, imageFile
	imageFile=tkFileDialog.askopenfilename(parent=root,title='Choose a file')
	if imageFile!=None:
		myPic=PhotoImage(file=imageFile)
		lbRolePrev.config(image=myPic)
		lbRolePrev.image = myPic
		
	else:
		print "error"
	
	
def setRoleName():
	global eRoleName
	roleName= eRoleName.get()
	
def myRoleWindow():
	global imageFile, tbQuotes, top, lbRolePrev, eRoleName, imageName, eRoleName
	top=Toplevel(root)
	
	lbRoleMo=Label(top,text="Role Model")
	lbRoleMo.grid(row=0,column=1)
	
	fRoleName=Frame(top)
	lbRoleName=Label(fRoleName,text="Name")
	lbRoleName.grid(row=0,column=0)
	eRoleName=Entry(fRoleName)
	eRoleName.grid(row=0,column=1)
	eRoleName.insert(END,imageName)
	bRoleButton=Button(fRoleName,text="Set Name",command=setRoleName())
	fRoleName.grid(row=1,column=0,sticky=W)
	
	lbPreview=Label(top,text="Preview")
	lbPreview.grid(row=2,column=0,sticky=W)
	
	#image1=PhotoImage(file="earth.gif")
	imageLab=PhotoImage(file=imageFile)
	if imageLab!=None:
		lbRolePrev=Label(top, image=imageLab)

		lbRolePrev.grid(row=3,column=0,sticky=W)

		lbRolePrev.image = imageLab
		lbRolePrev.grid(row=2,column=0,sticky=W)
	else:
		print "error"
	
	bSetPicture=Button(top,text="Load Picture", command=loadRoleModel)
	bSetPicture.grid(row=4,column=2)
	
	lbQuotes=Label(top,text="Quotes")
	lbQuotes.grid(row=4,column=0,sticky=W)
	tbQuotes=Text(top)
	tbQuotes.grid(row=5,column=0)
	
	for i in imageText:
		j= i+"\n"
		tbQuotes.insert(END, j)
	
	but=Button(top,text="commit",command=rolesCommit)
	but.grid(row=6,column=0)

def commitRoleModelsToFile():
	fileOpen = open(ROLE_FILE_NAME, 'wb')
	if fileOpen != None:
		pickle.dump(myRolesList, fileOpen)
		fileOpen.close()

def rolesCommit(): 
	global roleFile,imageText,tbQuotes, imageFile, imageName, top, eRoleName

	deterrentconfig = {}
	deterrentconfig['Name'] = eRoleName.get()
	deterrentconfig['ImagePath'] = imageFile
	deterrentconfig['QuotesList'] = tbQuotes.get(1.0, END).rstrip().split('\n')
	print deterrentconfig
	myRolesList.append(deterrentconfig)
	lbRoleModels.insert(END, deterrentconfig['Name'])
	commitRoleModelsToFile()
	top.destroy()

def rolesCommit_old():	
	global roleFile,imageText,tbQuotes, imageFile, imageName, top, eRoleName
	
	myQuotes=tbQuotes.get(1.0,END)
	g=0
	if roleFile!=None:
		roleFile=open(ROLE_FILE_NAME,'r')
		info=roleFile.readlines()
		roleFile.close()
		roleFile=open(ROLE_FILE_NAME,'w')
		for j in info:
			i=str(j).rstrip()
			
				
			
			if g==0:
				roleFile.write(i+"\n")
			elif i=="#":
				g=0
			elif i==imageName:
				g+=1
			
		imageName=eRoleName.get()
		lbRoleModels.insert(END,imageName)
		myRolesList.append(imageName)
		
		roleFile.write(imageName+"\n")
		roleFile.write(imageFile+"\n")
		textBox=tbQuotes.get(1.0,END)
		for n in textBox:
			roleFile.write(n)
		roleFile.write("#\n")
		roleFile.close()
		roleFile=open(ROLE_FILE_NAME,'r')
		info=roleFile.readlines()
		roleFile.close()
		top.destroy()
	else:
		print "error"
	
	
def roleWindowEDIT():
	global imageName, imageText, imageFile

	# TODO what if more than one entry is highlighted?
	selectedIndices = lbRoleModels.curselection()
	if len(selectedIndices) == 0:
		return
	
	roleModel = myRolesList[int(selectedIndices[0])]
	imageName = roleModel['Name']
	imageText = roleModel['QuotesList']
	imageFile = roleModel['ImagePath']
	myRoleWindow()


def	roleWindowEDIT_old():
	global roleFile,imageText,tbQuotes, imageFile, imageName, eRoleName
	
	mylist=lbRoleModels.curselection()
	if len(mylist) == 0:
		return
	else:
		print "Im going!"
			
	searchNum=mylist[0]
	searchVal=myRolesList[int(searchNum)]
	
	if roleFile!=None:
		roleFile=open(ROLE_FILE_NAME,'r')
		info=roleFile.readlines()
		roleFile.close()
		
		g=0
		imageText=[]
		for j in info:
			i=str(j).rstrip()
			if i == searchVal:
				imageName=i
				#eRoleName.delete(0,END)
				#eRoleName.insert(END)
				g+=1
			elif g==1:
				imageFile=i
				g+=1
			elif g>1:
				if i =="#":
					myRoleWindow()
					return
				imageText.append(i)
				
		
		
	else:
		print "error"
	
def	roleWindowADD():
	global imageText, imageFile, imageName
	imageGrap=0
	imageText=[]
	imageFile=""
	imageName=""
	myRoleWindow()
		

def roleListLoad():
	global myRolesList, lbRoleModels

	myRolesList = []
	lbRoleModels.delete(0, END)
	if os.path.isfile(ROLE_FILE_NAME):
		roleConfigFile = open(ROLE_FILE_NAME, 'r')
		if roleConfigFile != None:
			myRolesList = pickle.load(roleConfigFile)
			for role in myRolesList:
				lbRoleModels.insert(END, role['Name'])
			
def roleListLoad_old():
	global roleFile
	roleFile=open(ROLE_FILE_NAME,'r')
	if roleFile!=None:
		info=roleFile.readlines()
		g=0
		imageText=[]
		
		for j in info:
			if g== 0:
				i=str(j).rstrip()
				lbRoleModels.insert(END,i)
				myRolesList.append(i)
				g+=1
			elif i=="#":
				g=0
				
	roleFile.close()

def build_layout():
	global lbSiteList, SiteStr, intTimeType, BreakLengthStr
	global liTime, root, rbTimeRadios, intListType, lbRoleModels
	global roleName, roleText, roleFile, myRolesList, tbQuotes, imageFile
	global lbRolePrev, rbDetRadios, intDetType, entSite, bSite
	
	root= Tk()
	menubar = Menu(root)

	# create a pulldown menu, and add it to the menu bar
	filemenu = Menu(menubar, tearoff=0)
	filemenu.add_command(label="Open", command=openFile)
	filemenu.add_command(label="Save", command=saveFile)
	filemenu.add_separator()
	filemenu.add_command(label="Exit", command=root.quit)
	menubar.add_cascade(label="File", menu=filemenu)

	# Placeholder for Help menu
	helpmenu = Menu(menubar, tearoff=0)
	helpmenu.add_command(label="About")
	menubar.add_cascade(label="Help", menu=helpmenu)
	
	# display the menu
	root.config(menu=menubar)

	# create the website list
	frame = Frame(root)
	frame.grid(row=1,column=0)

	laWeb= Label(root, text="Websites")
	laWeb.grid(row=0, column=0)

	SiteStr = StringVar()
	entSite = Entry(frame, textvariable=SiteStr)
	entSite.grid(row=0, column=1)
	entSite.bind('<Key>', lookForEdit)

	laSite = Label(frame, text="Address")
	laSite.grid(row=0,column=0)

	bSite = Button(frame, text="Add Site", command=addSite)
	bSite.grid(row=0,column=2)

	lbSiteList=Listbox(root,selectmode=EXTENDED, exportselection=0)
	lbSiteList.grid(row=2, column=0)

	bRemoveSite = Button(root, text="Remove Site", command=removeSite)
	bRemoveSite.grid(row=3,column=0)

	poll() # Wait for user to click on site in list -- populate right side accordingly

	# Blacklist / Whitelist
	intListType= IntVar(value=1)
	fRadios=Frame(root)
	rbRadios.append(Radiobutton(fRadios,text="Whitelist", variable=intListType,value=LIST_TYPE_WHITELIST))
	rbRadios.append(Radiobutton(fRadios,text="Blacklist", variable=intListType,value=LIST_TYPE_BLACKLIST))
	rbRadios[0].grid(row=0, column=0)
	rbRadios[1].grid(row=0, column=1)
	fRadios.grid(row=5,column=0)

	# Blocking Method
	lTimeSection=Label(root, text="Blocking Method")
	lTimeSection.grid(row=0, column=4)

	fTimeList=Frame(root)
	fTimeList.grid(row=2, column=4, padx=15)

	intTimeType=IntVar()
	rbTimeRadios = []
	rbTimeRadios.append(Radiobutton(fTimeList,text="Deny Always", variable=intTimeType,value=TIME_TYPE_DENY_ALWAYS))
	rbTimeRadios.append(Radiobutton(fTimeList,text="Allow Breaks", variable=intTimeType,value=TIME_TYPE_ALLOW_BREAKS))
	rbTimeRadios.append(Radiobutton(fTimeList,text="Block Scheduling", variable=intTimeType,value=TIME_TYPE_BLOCK_SCHEDULING))
	rbTimeRadios[0].grid(row=0, column=0, sticky=W)
	rbTimeRadios[1].grid(row=1, column=0, sticky=W)
	rbTimeRadios[2].grid(row=3, column=0, sticky=W)

	# Blocking Method / Allow Breaks
	fBreakFrame=Frame(fTimeList)
	lbBreakLength=Label(fBreakFrame,text="Break Length")
	lbBreakLength.grid(row=2,column=0,sticky=E,padx=2)

	BreakLengthStr = StringVar()
	entBreakLength=Entry(fBreakFrame, textvariable=BreakLengthStr)
	entBreakLength.grid(row=2,column=1)
	fBreakFrame.grid(row=2,column=0,sticky=E,padx=20)

	# Blocking Method / Block Scheduling
	fTimeScroll=Frame(fTimeList)
	fTimeScroll.grid(row=4,column=0)
	scTime = Scrollbar(fTimeScroll, orient=VERTICAL)
	liTime = Listbox(fTimeScroll, selectmode=EXTENDED,yscrollcommand=scTime.set, exportselection=0)
	liTime.grid(row=0, column=0, sticky=N+S, rowspan=1)

	scTime.config(command=liTime.yview)
	scTime.grid(row=0, column=1, rowspan=1, sticky=N+S)

	for item in ["12 am", "1 am", "2 am", "3 am", "4 am", "5 am", "6 am",
		     "7 am", "8 am", "9 am", "10 am", "11 am", "12 pm", "1 pm", "2 pm",
		     "3 pm", "4  pm", "5 pm", "6 pm", "7 pm", "8 pm", "9 pm", "10 pm", 
		     "11 pm"]:
		liTime.insert(END, item)

		
	
	#Deterrents
	
	intDetType=IntVar()
	
	lbDet=Label(root,text="Deterrents")
	lbDet.grid(row=0,column=6)
	fDets=Frame(root)
	rbDetRadios=[]
	rbDetRadios.append(Radiobutton(fDets,text="Only Block", variable=intDetType,value=DET_TYPE_DENY))
	rbDetRadios.append(Radiobutton(fDets,text="Type Deterrent", variable=intDetType,value=DET_TYPE_TYPE))
	rbDetRadios.append(Radiobutton(fDets,text="Role Models", variable=intDetType,value=DET_TYPE_ROLES))

	rbDetRadios[0].grid(row=0,column=0,sticky=W)
	rbDetRadios[1].grid(row=1,column=0,sticky=W)
	rbDetRadios[2].grid(row=2,column=0,sticky=W)

	lbRoleModels= Listbox(fDets, exportselection=0)
	lbRoleModels.grid(row=3,column=0)
	
	roleFrame=Frame(fDets)
	bAddWindow=Button(roleFrame,text="Add New")
	bAddWindow.config(command=roleWindowADD)
	bAddWindow.grid(row=0,column=0)
	bEditWindow=Button(roleFrame,text="Edit Selection")
	bEditWindow.config(command=roleWindowEDIT)
	bEditWindow.grid(row=0,column=1)
	roleFrame.grid(row=4,column=0)

	fDets.grid(row=2,column=6)	
	roleListLoad()

def main():
	build_layout()
	mainloop()

if __name__ == "__main__":
	main()

