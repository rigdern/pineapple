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
DET_TYPE_EXPLAIN = 3

PROJECT_DIR="./proj/"
PROJECT_EXT=".cf"

mySites=[]
#rbRadios=[]
picRole=0
lastselection = None
myRolesList=[]
iProjType=0


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
		siteconfig['BlockConfig']['TimeBetweenBreaks']=WaitTimeStr.get()
	elif blocktype == TIME_TYPE_BLOCK_SCHEDULING:
		allowed_blocks=liTime.curselection()
		siteconfig['BlockConfig']['AllowedTime'] = []
		for allowed_time in allowed_blocks:
			siteconfig['BlockConfig']['AllowedTime'].append(allowed_time)

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
	lbSiteList.insert(END, siteconfig['url'])
	clearAllFields()

def openFile():
	global mySites
        infile = tkFileDialog.askopenfile(parent=setting,mode='rb',title='Choose a configuration file to open')
	if infile != None:
		mySites = pickle.load(infile)
		if mySites == None or len(mySites) == 0:
			return
		print mySites
		lbSiteList.delete(0, END)
		for k in mySites:
			lbSiteList.insert(END, k['url'])

def saveFile():
	#fileName = tkFileDialog.asksaveasfilename(parent=setting, title="Save the configuration file as...")
	global eProjName
	fileName = eProjName.get()
	if len(fileName) > 1:
		outfile = open(PROJECT_DIR + '/' + fileName, 'wb')
		pickle.dump(mySites, outfile)
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
		WaitTimeStr.set(str(configobj['BlockConfig']['TimeBetweenBreaks']))
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

def clearAllFields():
	intDetType.set(0)
	intTimeType.set(0)
	BreakLengthStr.set('')
	WaitTimeStr.set('')
	liTime.select_clear(0, END)
	lbRoleModels.selection_clear(0, END)

def loadRoleModel():
#<<<<<<< HEAD
#	global lbRolePrev
#	fileM=tkFileDialog.askopenfilename(parent=setting,title='Choose a file')
#	print fileM
#	if fileM!=None:
#		myPic=PhotoImage(file=fileM)
#=======
	global lbRolePrev, imageFile
	imageFile=tkFileDialog.askopenfilename(parent=setting,title='Choose a file')
	if imageFile!=None:
		myPic=PhotoImage(file=imageFile)
#>>>>>>> 912814b6d4c9c44d2fffb8f7b4d3e953a44b4b29
		lbRolePrev.config(image=myPic)
		lbRolePrev.image = myPic
		
	else:
		print "error"
	
	
def setRoleName():
	global eRoleName
	roleName= eRoleName.get()
	
def myRoleWindow():
#<<<<<<< HEAD
	global imageFile, tbQuotes, top, lbRolePrev, eRoleName, imageName
	top=Toplevel(setting)
#=======
#	global imageFile, tbQuotes, top, lbRolePrev, eRoleName, imageName, eRoleName
#	top=Toplevel(root)
#>>>>>>> 912814b6d4c9c44d2fffb8f7b4d3e953a44b4b29
	
	lbRoleMo=Label(top,text="Role Model")
	lbRoleMo.grid(row=0,column=1)
	
	fRoleName=Frame(top)
	lbRoleName=Label(fRoleName,text="Name")
	lbRoleName.grid(row=0,column=0)
	eRoleName=Entry(fRoleName)
	eRoleName.grid(row=0,column=1)
	eRoleName.insert(END,imageName)
	bRoleButton=Button(fRoleName,text="Set Name",command=setRoleName)
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
	
	bSetPicture=Button(top,text="Select Picture", command=loadRoleModel)
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
#<<<<<<< HEAD
#	global lbSiteList, SiteStr, intTimeType, BreakLengthStr
	global liTime, setting, rbTimeRadios, intListType, lbRoleModels
	global roleName, roleText, roleFile, myRolesList, tbQuotes, imageFile
#	global lbRolePrev, projects, eProjName
#=======
	global lbSiteList, SiteStr, intTimeType, BreakLengthStr, WaitTimeStr
#	global liTime, root, rbTimeRadios, intListType, lbRoleModels
	global roleName, roleText, roleFile, myRolesList, tbQuotes, imageFile
	global lbRolePrev, rbDetRadios, intDetType, entSite, bSite, projects, eProjName, rbRadios
#>>>>>>> 912814b6d4c9c44d2fffb8f7b4d3e953a44b4b29
	
	setting= Toplevel(projects)
	menubar = Menu(setting)

	# create a pulldown menu, and add it to the menu bar
	filemenu = Menu(menubar, tearoff=0)
	filemenu.add_command(label="Open", command=openFile)
	filemenu.add_command(label="Save", command=saveFile)
	filemenu.add_separator()
	filemenu.add_command(label="Exit", command=setting.quit)
	menubar.add_cascade(label="File", menu=filemenu)

	# Placeholder for Help menu
	helpmenu = Menu(menubar, tearoff=0)
	helpmenu.add_command(label="About")
	menubar.add_cascade(label="Help", menu=helpmenu)
	
	# display the menu
	setting.config(menu=menubar)

	# create the website list
	fWebsites = Frame(setting)
	frame = Frame(fWebsites)
	frame.grid(row=2,column=0)

	laWeb= Label(fWebsites, text="Websites")
	laWeb.grid(row=0, column=0)

	SiteStr = StringVar()
	entSite = Entry(frame, textvariable=SiteStr)
	entSite.grid(row=0, column=1)
	entSite.bind('<Key>', lookForEdit)

	laSite = Label(frame, text="Address")
	laSite.grid(row=0,column=0)

	bSite = Button(frame, text="Add Site", command=addSite)
	bSite.grid(row=0,column=2)

#<<<<<<< HEAD
	lbSiteList=Listbox(fWebsites,selectmode=EXTENDED, exportselection=0)
	lbSiteList.grid(row=3, column=0)
#=======
#	lbSiteList=Listbox(root,selectmode=EXTENDED, exportselection=0)
#	lbSiteList.grid(row=2, column=0)
#>>>>>>> 912814b6d4c9c44d2fffb8f7b4d3e953a44b4b29

	bRemoveSite = Button(fWebsites, text="Remove Site", command=removeSite)
	bRemoveSite.grid(row=4,column=0)
	
	

	poll() # Wait for user to click on site in list -- populate right side accordingly

	# Blacklist / Whitelist
	intListType= IntVar(value=1)
	fRadios=Frame(fWebsites)
	rbRadios = []
	rbRadios.append(Radiobutton(fRadios,text="Whitelist", variable=intListType,value=LIST_TYPE_WHITELIST))
	rbRadios.append(Radiobutton(fRadios,text="Blacklist", variable=intListType,value=LIST_TYPE_BLACKLIST))
	rbRadios[0].grid(row=0, column=0)
	rbRadios[1].grid(row=0, column=1)
	fRadios.grid(row=6,column=0)

	fWebsites.grid(row=3,column=0)
	
	
	# Blocking Method
	fBlock= Frame(setting)
	lTimeSection=Label(fBlock, text="Blocking Method")
	lTimeSection.grid(row=1, column=4)

	fTimeList=Frame(fBlock)
	fTimeList.grid(row=3, column=4, padx=15)

	intTimeType=IntVar()
	rbTimeRadios = []
	rbTimeRadios.append(Radiobutton(fTimeList,text="Deny Always", variable=intTimeType,value=TIME_TYPE_DENY_ALWAYS))
	rbTimeRadios.append(Radiobutton(fTimeList,text="Allow Breaks", variable=intTimeType,value=TIME_TYPE_ALLOW_BREAKS))
	rbTimeRadios.append(Radiobutton(fTimeList,text="Block Scheduling", variable=intTimeType,value=TIME_TYPE_BLOCK_SCHEDULING))
	rbTimeRadios[0].grid(row=0, column=0, sticky=W)
	rbTimeRadios[1].grid(row=1, column=0, sticky=W)
	rbTimeRadios[2].grid(row=4, column=0, sticky=W)

	# Blocking Method / Allow Breaks
	fBreakFrame=Frame(fTimeList)
	lbBreakLength=Label(fBreakFrame,text="Break Length")
	lbBreakLength.grid(row=2,column=0,sticky=E,padx=2)

	BreakLengthStr = StringVar()
	entBreakLength=Entry(fBreakFrame, textvariable=BreakLengthStr)
	entBreakLength.grid(row=2,column=1)
#<<<<<<< HEAD
#	fBreakFrame.grid(row=3,column=0,sticky=E,padx=20)
#=======

	lbBreakWaitTime = Label(fBreakFrame, text="Time Between Breaks")
	lbBreakWaitTime.grid(row=3,column=0,sticky=E,padx=2)
	WaitTimeStr = StringVar()
	entWaitTime = Entry(fBreakFrame, textvariable=WaitTimeStr)
	entWaitTime.grid(row=3,column=1)
#	fBreakFrame.grid(row=2,column=0,sticky=E,padx=20)
#>>>>>>> 912814b6d4c9c44d2fffb8f7b4d3e953a44b4b29

	fBreakFrame.grid(row=3,column=0,sticky=E,padx=20)


	# Blocking Method / Block Scheduling
	fTimeScroll=Frame(fTimeList)
	fTimeScroll.grid(row=6,column=0)
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

	fBlock.grid(row=3,column=4)
	
	#Deterrents
	
	fDeterrents= Frame(setting)
	intDetType=IntVar()
	
#<<<<<<< HEAD
	lbDet=Label(fDeterrents,text="Deterrents")
	lSpace=Label(fDeterrents,text="")
	lSpace.grid(row=0,column=0)
	lbDet.grid(row=1,column=6)
	fDets=Frame(fDeterrents)
#=======
#	lbDet=Label(root,text="Deterrents")
#	lbDet.grid(row=0,column=6)
#	fDets=Frame(root)
#>>>>>>> 912814b6d4c9c44d2fffb8f7b4d3e953a44b4b29
	rbDetRadios=[]
	rbDetRadios.append(Radiobutton(fDets,text="Only Block", variable=intDetType,value=DET_TYPE_DENY))
	rbDetRadios.append(Radiobutton(fDets,text="Type Deterrent", variable=intDetType,value=DET_TYPE_TYPE))
	rbDetRadios.append(Radiobutton(fDets,text="Explain Value", variable=intDetType, value=DET_TYPE_EXPLAIN))
	rbDetRadios.append(Radiobutton(fDets,text="Role Models", variable=intDetType,value=DET_TYPE_ROLES))

	rbDetRadios[0].grid(row=0,column=0,sticky=W)
	rbDetRadios[1].grid(row=1,column=0,sticky=W)
	rbDetRadios[2].grid(row=2,column=0,sticky=W)
	rbDetRadios[3].grid(row=3,column=0,sticky=W)

	lbRoleModels= Listbox(fDets, exportselection=0)
	lbRoleModels.grid(row=4,column=0)
	
	roleFrame=Frame(fDets)
	bAddWindow=Button(roleFrame,text="Add New")
	bAddWindow.config(command=roleWindowADD)
	bAddWindow.grid(row=0,column=0)
	bEditWindow=Button(roleFrame,text="Edit Selection")
	bEditWindow.config(command=roleWindowEDIT)
	bEditWindow.grid(row=0,column=1)
	roleFrame.grid(row=5,column=0)
#<<<<<<< HEAD
	
	fDets.grid(row=3,column=6)
	fDeterrents.grid(row=3,column=6)
	
	
#=======

#	fDets.grid(row=2,column=6)	
#>>>>>>> 912814b6d4c9c44d2fffb8f7b4d3e953a44b4b29
	roleListLoad()
	
	fProjInfo = Frame(setting)
	lProjName= Label(fProjInfo, text="Project Name")
	eProjName=Entry(fProjInfo)
	bProjCommit = Button(fProjInfo,text="Commit Changes",command=saveFile)
	lProjName.grid(row=0,column=0)
	eProjName.grid(row=0,column=1)
	bProjCommit.grid(row=0,column=2,)
	fProjInfo.grid(row=0,column=4)
	
	
	if iProjType == 1:
		openProject()
	elif iProjType ==2:
		pass
	else:
		assert ( 0) #should not come here

def dEditProj():
	global iProjType
	iProjType=1
	build_layout()
	
def dNewProj():
	global iProjType
	iProjType=2
	build_layout()
	
def dDeleteProj():
	pass

	
def projectWindow():
	global projects, lbProjects, iProjType
	projects= Tk()
	
	
	
	lProjects=Label(projects, text="Projects")
	lProjects.grid(row=0,column=0,sticky=W, )
	lbProjects = Listbox(projects)
	lbProjects.grid(row=1,column=0, pady=3, padx=3)
	lbProjects.bind("<Double-Button-1>", lambda e: dEditProj())
	frame=Frame(projects)
	bProjectsE=Button(frame,text="Edit",command=dEditProj)
	bProjectsN=Button(frame,text="New",command=dNewProj)
	bProjectsD=Button(frame,text="Delete",command=dDeleteProj)
	bProjectsE.grid(row=0,column=0)
	bProjectsN.grid(row=0,column=1)
	bProjectsD.grid(row=0,column=2)
	frame.grid(row=5,column=0)
	
	getProjects()
	
	mainloop()
	
def openProject():
	global lbProjects, projectsList, lbSiteList, mySites
	pjname=projectsList[int(lbProjects.curselection()[0])]
	infile = open(PROJECT_DIR+pjname)
	if infile != None:
		mySites = pickle.load(infile)
		if mySites == None or len(mySites) == 0:
			return
		if lbSiteList == None:
			lbSiteList=Listbox()
		lbSiteList.delete(0, END)
		for k in mySites:
			lbSiteList.insert(END, k['url'])
		eProjName.delete(0, END)
		eProjName.insert(END, pjname)
	
def getProjects():
	global lbProjects, projectsList, projects
	
	
	projectsList=[]
	lbProjects.delete(0,END)
	pro=os.listdir(PROJECT_DIR)
	
	for i in pro:
		file=open(PROJECT_DIR+i)
		projectsList.append(i)
		lbProjects.insert(END,i)
	
	
	#build_layout()
	#mainloop()
	
def main():
	#build_layout()
	projectWindow()
	

if __name__ == "__main__":
	main()

