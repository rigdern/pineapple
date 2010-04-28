from Tkinter import *
from constants import *

import tkFileDialog
import os
import pickle



class ProjectConfigDialog():
    def __init__(self, projconfig):
        self.projectconfig = projconfig
        self.lastselection = None
        self.build_layout()

    def removeSite(self): 
	site=self.SiteStr.get()
	oldSites=self.lbSiteList.curselection()
	for i in oldSites:
            if self.projectconfig.mySites['url'] == site:
		self.lbSiteList.delete(i)
		del self.projectconfig.mySites[int(i)]

    def roleListLoad(self): 
	self.projectconfig.myRolesList = []
	self.lbRoleModels.delete(0, END)
	if os.path.isfile(ROLE_FILE_NAME):
		roleConfigFile = open(ROLE_FILE_NAME, 'r')
		if roleConfigFile != None:
			self.projectconfig.myRolesList = pickle.load(roleConfigFile)
			for role in self.projectconfig.myRolesList:
				self.lbRoleModels.insert(END, role['Name'])

    def loadRoleModel(self): 
	self.imageFile=tkFileDialog.askopenfilename(parent=self.setting,title='Choose a file')
	if self.imageFile!=None:
		myPic=PhotoImage(file=self.imageFile)
		self.lbRolePrev.config(image=myPic)
		self.lbRolePrev.image = myPic
		
	else:
		print "error"

    def removeRoleModel(self):
        selection = self.lbRoleModels.curselection()
        if len(selection) != 1:
            return

        selectedIndex = int(selection[0])
        self.lbRoleModels.delete(selectedIndex)
        self.projectconfig.myRolesList.pop(selectedIndex)
        self.commitRoleModelsToFile()

    def clearAllFields(self): 
	self.intDetType.set(0)
	self.intTimeType.set(0)
	self.BreakLengthStr.set('')
	self.liTime.select_clear(0, END)
	self.lbRoleModels.selection_clear(0, END)

    def roleWindowEDIT(self):
	# TODO what if more than one entry is highlighted?
	selectedIndices = self.lbRoleModels.curselection()
	if len(selectedIndices) == 0:
		return
	
	roleModel = self.projectconfig.myRolesList[int(selectedIndices[0])]
	self.imageName = roleModel['Name']
	self.imageText = roleModel['QuotesList']
	self.imageFile = roleModel['ImagePath']
	self.myRoleWindow()

    def poll(self): 
	currentselection = self.lbSiteList.curselection()
	if currentselection != self.lastselection or self.clickwaiting:
		self.lastselection = currentselection
                self.list_selection_changed(currentselection)
                self.set_click_waiting(0)
	self.lbSiteList.after(200, self.poll)

    def list_selection_changed(self, selection): 
	if len(selection) < 1:
		return
	self.BreakLengthStr.set('')
	configobj = self.projectconfig.mySites[int(selection[0])]
	self.liTime.select_clear(0, END)
	self.SiteStr.set(configobj['url'])
	blockmethod = configobj['BlockConfig']['Method']
	self.rbTimeRadios[blockmethod].select()
	if (blockmethod == TIME_TYPE_ALLOW_BREAKS):
		self.BreakLengthStr.set(str(configobj['BlockConfig']['BreakLength']))
	elif (blockmethod == TIME_TYPE_BLOCK_SCHEDULING):
		breaks = configobj['BlockConfig']['AllowedTime']
		for allowedtime in breaks:
			self.liTime.selection_set(allowedtime)

	deterrentmethod = configobj['Deterrents']['Method']
	self.intDetType.set(deterrentmethod)
	if deterrentmethod == DET_TYPE_ROLES:
		roleName = configobj['Deterrents']['RoleModelName']
		for i in range(0, len(self.projectconfig.myRolesList)):
			if self.projectconfig.myRolesList[i]['Name'] == roleName:
				self.lbRoleModels.selection_set(i)
	self.lookForEdit(1)

    def commitRoleModelsToFile(self): 
	fileOpen = open(ROLE_FILE_NAME, 'wb')
	if fileOpen != None:
		pickle.dump(self.projectconfig.myRolesList, fileOpen)
		fileOpen.close()

    def roleWindowADD(self): 
	self.imageText=[]
	self.imageFile=""
	self.imageName=""
	self.myRoleWindow()
		
    def lookForEdit(self, setnow): 
        if setnow:
            for site in self.projectconfig.mySites:
		if self.SiteStr.get() == site['url']:
                    self.bSite.config(text="Edit Site")
                    return
        
        self.bSite.config(text="Add Site")

    def rolesCommit(self): 
	deterrentconfig = {}
	deterrentconfig['Name'] = self.eRoleName.get()
	deterrentconfig['ImagePath'] = self.imageFile
	deterrentconfig['QuotesList'] = self.tbQuotes.get(1.0, END).rstrip().split('\n')

        found = 0
	for i in range(0, len(self.projectconfig.myRolesList)):
            if deterrentconfig['Name'] == self.projectconfig.myRolesList[i]['Name']:
                self.projectconfig.myRolesList[i] = deterrentconfig
                found = 1
                break
        
        if not found:
                self.projectconfig.myRolesList.append(deterrentconfig)
                self.lbRoleModels.insert(END, deterrentconfig['Name'])
	        
        self.commitRoleModelsToFile()
	self.top.destroy()


    def myRoleWindow(self): 
	self.top=Toplevel(self.setting)
	
	lbRoleMo=Label(self.top,text="Role Model")
	lbRoleMo.grid(row=0,column=1)
	
	fRoleName=Frame(self.top)
	lbRoleName=Label(fRoleName,text="Name")
	lbRoleName.grid(row=0,column=0)
	self.eRoleName=Entry(fRoleName)
	self.eRoleName.grid(row=0,column=1)
	self.eRoleName.insert(END,self.imageName)
	fRoleName.grid(row=1,column=0,sticky=W)
	
	lbPreview=Label(self.top,text="Preview")
	lbPreview.grid(row=2,column=0,sticky=W)
	
        self.lbRolePrev=Label(self.top)
        self.lbRolePrev.grid(row=2,column=0,sticky=W)
        
        try:
            imageLab=PhotoImage(file=self.imageFile)
            self.lbRolePrev.config(image=imageLab)
            self.lbRolePrev.image = imageLab
        except:
            print "error loading image"
	
	bSetPicture=Button(self.top,text="Select Picture", command=self.loadRoleModel)
	bSetPicture.grid(row=4,column=2)
	
	lbQuotes=Label(self.top,text="Quotes")
	lbQuotes.grid(row=4,column=0,sticky=W)
	self.tbQuotes=Text(self.top)
	self.tbQuotes.grid(row=5,column=0)
	
	for i in self.imageText:
		j= i+"\n"
		self.tbQuotes.insert(END, j)
	
	but=Button(self.top,text="commit",command=self.rolesCommit)
	but.grid(row=6,column=0)

    def set_click_waiting(self, num):
        print "setting to ", num
        self.clickwaiting = num

    def build_layout(self):
	self.setting= Toplevel(self.projectconfig.projectsWindow)
	menubar = Menu(self.setting)

	# create a pulldown menu, and add it to the menu bar
	filemenu = Menu(menubar, tearoff=0)
#	filemenu.add_command(label="Open", command=self.projectconfig.openFile)
#	filemenu.add_command(label="Save", command=self.projectconfig.saveFile)
	filemenu.add_separator()
	filemenu.add_command(label="Exit", command=self.setting.quit)
	menubar.add_cascade(label="File", menu=filemenu)

	# Placeholder for Help menu
	helpmenu = Menu(menubar, tearoff=0)
	helpmenu.add_command(label="About")
	menubar.add_cascade(label="Help", menu=helpmenu)
	
	# display the menu
	self.setting.config(menu=menubar)

	# create the website list
	fWebsites = Frame(self.setting)
	frame = Frame(fWebsites)
	frame.grid(row=2,column=0)

	laWeb= Label(fWebsites, text="Websites")
	laWeb.grid(row=0, column=0)

        self.clickwaiting = 0

	self.SiteStr = StringVar()
	entSite = Entry(frame, textvariable=self.SiteStr)
	entSite.grid(row=0, column=1)
	entSite.bind('<Key>', lambda e: self.lookForEdit(0))

	laSite = Label(frame, text="Address")
	laSite.grid(row=0,column=0)

	self.bSite = Button(frame, text="Add Site", command=self.projectconfig.addSite)
	self.bSite.grid(row=0,column=2)

	self.lbSiteList=Listbox(fWebsites,selectmode=EXTENDED, exportselection=0)
	self.lbSiteList.grid(row=3, column=0)
        self.lbSiteList.bind('<Button-1>', lambda e: self.set_click_waiting(1))

	bRemoveSite = Button(fWebsites, text="Remove Site", command=self.removeSite)
	bRemoveSite.grid(row=4,column=0)
	
	

	self.poll() # Wait for user to click on site in list -- populate right side accordingly

	# Blacklist / Whitelist
	self.intListType= IntVar(value=1)
	"""fRadios=Frame(fWebsites)
	rbRadios = []
	rbRadios.append(Radiobutton(fRadios,text="Whitelist", variable=self.intListType,value=LIST_TYPE_WHITELIST))
	rbRadios.append(Radiobutton(fRadios,text="Blacklist", variable=self.intListType,value=LIST_TYPE_BLACKLIST))
	rbRadios[0].grid(row=0, column=0)
	rbRadios[1].grid(row=0, column=1)
	fRadios.grid(row=6,column=0)
        """

	fWebsites.grid(row=3,column=0)
	
	
	# Blocking Method
	fBlock= Frame(self.setting)
	lTimeSection=Label(fBlock, text="Blocking Method")
	lTimeSection.grid(row=1, column=4)

	fTimeList=Frame(fBlock)
	fTimeList.grid(row=3, column=4, padx=15)

	self.intTimeType=IntVar()
	self.rbTimeRadios = []
        self.rbTimeRadios.append(Radiobutton(fTimeList,text="Deter Once", variable=self.intTimeType,value=TIME_TYPE_DENY_ALWAYS))
	self.rbTimeRadios.append(Radiobutton(fTimeList,text="Allow Breaks", variable=self.intTimeType,value=TIME_TYPE_ALLOW_BREAKS))
	self.rbTimeRadios.append(Radiobutton(fTimeList,text="Block Scheduling", variable=self.intTimeType,value=TIME_TYPE_BLOCK_SCHEDULING))
	self.rbTimeRadios[0].grid(row=0, column=0, sticky=W)
	self.rbTimeRadios[1].grid(row=1, column=0, sticky=W)
	self.rbTimeRadios[2].grid(row=4, column=0, sticky=W)

	# Blocking Method / Allow Breaks
	fBreakFrame=Frame(fTimeList)
	lbBreakLength=Label(fBreakFrame,text="Break Length")
	lbBreakLength.grid(row=2,column=0,sticky=E,padx=2)

	self.BreakLengthStr = StringVar()
	entBreakLength=Entry(fBreakFrame, textvariable=self.BreakLengthStr)
	entBreakLength.grid(row=2,column=1)

	fBreakFrame.grid(row=3,column=0,sticky=E,padx=20)

	# Blocking Method / Block Scheduling
	fTimeScroll=Frame(fTimeList)
	fTimeScroll.grid(row=6,column=0)
	scTime = Scrollbar(fTimeScroll, orient=VERTICAL)
	self.liTime = Listbox(fTimeScroll, selectmode=EXTENDED,yscrollcommand=scTime.set, exportselection=0)
	self.liTime.grid(row=0, column=0, sticky=N+S, rowspan=1)

	scTime.config(command=self.liTime.yview)
	scTime.grid(row=0, column=1, rowspan=1, sticky=N+S)

	for item in ["12 am", "1 am", "2 am", "3 am", "4 am", "5 am", "6 am",
		     "7 am", "8 am", "9 am", "10 am", "11 am", "12 pm", "1 pm", "2 pm",
		     "3 pm", "4  pm", "5 pm", "6 pm", "7 pm", "8 pm", "9 pm", "10 pm", 
		     "11 pm"]:
		self.liTime.insert(END, item)

	fBlock.grid(row=3,column=4)
	
	#Deterrents
	
	fDeterrents= Frame(self.setting)
	self.intDetType=IntVar()
	
	lbDet=Label(fDeterrents,text="Deterrents")
	lSpace=Label(fDeterrents,text="")
	lSpace.grid(row=0,column=0)
	lbDet.grid(row=1,column=6)
	fDets=Frame(fDeterrents)

	rbDetRadios=[]
	rbDetRadios.append(Radiobutton(fDets,text="Only Block", variable=self.intDetType,value=DET_TYPE_DENY))
	rbDetRadios.append(Radiobutton(fDets,text="Type Deterrent", variable=self.intDetType,value=DET_TYPE_TYPE))
	rbDetRadios.append(Radiobutton(fDets,text="Explain Value", variable=self.intDetType, value=DET_TYPE_EXPLAIN))
	rbDetRadios.append(Radiobutton(fDets,text="Role Models", variable=self.intDetType,value=DET_TYPE_ROLES))

	rbDetRadios[0].grid(row=0,column=0,sticky=W)
	rbDetRadios[1].grid(row=1,column=0,sticky=W)
	rbDetRadios[2].grid(row=2,column=0,sticky=W)
	rbDetRadios[3].grid(row=3,column=0,sticky=W)

	self.lbRoleModels= Listbox(fDets, exportselection=0)
	self.lbRoleModels.grid(row=4,column=0)
        self.lbRoleModels.bind("<Double-Button-1>", lambda e: self.roleWindowEDIT())
	
	roleFrame=Frame(fDets)
	bAddWindow=Button(roleFrame,text="Add New")
	bAddWindow.config(command=self.roleWindowADD)
	bAddWindow.grid(row=0,column=0)
	bEditWindow=Button(roleFrame,text="Edit Selection")
	bEditWindow.config(command=self.roleWindowEDIT)
	bEditWindow.grid(row=0,column=1)
	bDelete=Button(roleFrame,text="Delete Role Model")
	bDelete.config(command=self.removeRoleModel)
	bDelete.grid(row=0,column=2)

	roleFrame.grid(row=5,column=0)
	
	fDets.grid(row=3,column=6)
	fDeterrents.grid(row=3,column=6)
	
	
	self.roleListLoad()
	
	fProjInfo = Frame(self.setting)
	lProjName= Label(fProjInfo, text="Project Name")
	self.eProjName=Entry(fProjInfo)
	bProjCommit = Button(fProjInfo,text="Commit Changes",command=self.projectconfig.saveFile)
	lProjName.grid(row=0,column=0)
	self.eProjName.grid(row=0,column=1)
	bProjCommit.grid(row=0,column=2,)
	fProjInfo.grid(row=0,column=4)
	
	
