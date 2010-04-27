# file: conf.py


from Tkinter import *
from projectconfigdialog import *
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

picRole=0

ROLE_FILE_NAME="myRoles"

class ProjectConfig:
    def __init__(self):
        self.mySites = []
        self.myRolesList = []
        self.pcd = None
        self.projectWindow()

    def addSite(self): 
        siteconfig = {}
        siteconfig['url'] = self.pcd.SiteStr.get()
        self.pcd.SiteStr.set('')
        siteconfig['BlockConfig'] = {}
        siteconfig['BlackWhiteList'] = self.pcd.intListType.get()
        blocktype = self.pcd.intTimeType.get()
        siteconfig['BlockConfig']['Method'] = blocktype
        if blocktype == TIME_TYPE_ALLOW_BREAKS:
            siteconfig['BlockConfig']['BreakLength']=self.pcd.BreakLengthStr.get()
        elif blocktype == TIME_TYPE_BLOCK_SCHEDULING:
            allowed_blocks=self.pcd.liTime.curselection()
            siteconfig['BlockConfig']['AllowedTime'] = []
            for allowed_time in allowed_blocks:
                siteconfig['BlockConfig']['AllowedTime'].append(allowed_time)

        dettype = self.pcd.intDetType.get()
        siteconfig['Deterrents'] = {}
        siteconfig['Deterrents']['Method'] = dettype
        if dettype == DET_TYPE_ROLES:
            rowindex = self.pcd.lbRoleModels.curselection()
            if len(rowindex) != 1:
                print "error: must select a role model"
                return
            siteconfig['Deterrents']['RoleModelName'] = self.myRolesList[int(rowindex[0])]['Name']

        print siteconfig

        self.mySites.append(siteconfig)
        self.pcd.lbSiteList.insert(END, siteconfig['url'])
        self.pcd.clearAllFields()

    def openFile(self): 
        infile = tkFileDialog.askopenfile(parent=setting,mode='rb',title='Choose a configuration file to open')
	if infile != None:
            self.mySites = pickle.load(infile)
            if self.mySites == None or len(self.mySites) == 0:
                return
            print self.mySites
            self.pcd.lbSiteList.delete(0, END)
            for k in self.mySites:
                self.pcd.lbSiteList.insert(END, k['url'])

    def saveFile(self): 
	fileName = self.pcd.eProjName.get()
	if len(fileName) > 1:
            outfile = open(PROJECT_DIR + fileName, 'wb')
            pickle.dump(self.mySites, outfile)
            outfile.close()      	

    def dEditProj(self):
	self.pcd = ProjectConfigDialog(self)
        self.openProject()

    def dNewProj(self):
        self.pcd = ProjectConfigDialog(self)
	
    def dDeleteProj(self):
	pass

    def dEmployProj(self):
	# TODO call Adam's program from here
	pass
	
    def projectWindow(self):

	self.projectsWindow = Tk()
	
	lProjects=Label(self.projectsWindow, text="Projects")
	lProjects.grid(row=0,column=0,sticky=W, )
	self.lbProjects = Listbox(self.projectsWindow)
	self.lbProjects.grid(row=1,column=0, pady=3, padx=3)
	self.lbProjects.bind("<Double-Button-1>", lambda e: self.dEditProj())
	frame=Frame(self.projectsWindow)
	bProjectsE=Button(frame,text="Edit",command=self.dEditProj)
	bProjectsN=Button(frame,text="New",command=self.dNewProj)
	bProjectsD=Button(frame,text="Delete",command=self.dDeleteProj)
	bProjectsEm=Button(frame, text="Employ", command=self.dEmployProj)
	bProjectsE.grid(row=0,column=0)
	bProjectsN.grid(row=0,column=1)
	bProjectsD.grid(row=0,column=2)
	bProjectsEm.grid(row=0,column=3)
	frame.grid(row=5,column=0)
	
	self.getProjects()
	
	mainloop()
	
    def openProject(self):
	pjname=self.projectsList[int(self.lbProjects.curselection()[0])]
	infile = open(PROJECT_DIR+pjname)
	if infile != None:
            self.mySites = pickle.load(infile)
            if self.mySites == None or len(self.mySites) == 0:
                return
            if self.pcd.lbSiteList == None:
                self.pcd.lbSiteList=Listbox()
            self.pcd.lbSiteList.delete(0, END)
            for k in self.mySites:
                self.pcd.lbSiteList.insert(END, k['url'])
            self.pcd.eProjName.delete(0, END)
            self.pcd.eProjName.insert(END, pjname)

    def getProjects(self):
	self.projectsList=[]
	self.lbProjects.delete(0,END)
	pro=os.listdir(PROJECT_DIR)
	
	for i in pro:
            file=open(PROJECT_DIR+i)
            self.projectsList.append(i)
            self.lbProjects.insert(END,i)
	
		
def main():
    pj = ProjectConfig()
	

if __name__ == "__main__":
	main()

