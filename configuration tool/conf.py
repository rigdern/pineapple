""" conf.py

ProjectConfig class - manage configuration information for a specific project. Handle I/O with the configuration file. Also interacts with instance of ProjectConfigDialog which acts as the interface for the configuration of a project.

ProjectConfig creates the menu with a list of all projects and the options to add/edit/employ/delete


"""

import sys
sys.path += ['..']

from Tkinter import *
from projectconfigdialog import *
from constants import *
from subprocess import Popen
import tkFileDialog
import os
import pickle


class ProjectConfig:
    def __init__(self):
        self.mySites = []
        self.myRolesList = []
        self.pcd = None
        self.web_server_process = None
        self.projectWindow()

    """ Called when user enters URL in site field and hits "Add Site" or "Edit Site"
    Constructs object with all information about site policy saves until commit takes place"""
    def addSite(self): 
        siteconfig = {}
        siteconfig['url'] = self.pcd.SiteStr.get()
        siteconfig['BlockConfig'] = {}
        siteconfig['BlackWhiteList'] = self.pcd.intListType.get()
        blocktype = self.pcd.intTimeType.get()
        siteconfig['BlockConfig']['Method'] = blocktype
        if blocktype == TIME_TYPE_ALLOW_BREAKS:
            siteconfig['BlockConfig']['BreakLength'] = self.pcd.BreakLengthStr.get()
            siteconfig['BlockConfig']['TimeBetweenBreaks'] = self.pcd.WaitTimeStr.get()
        elif blocktype == TIME_TYPE_BLOCK_SCHEDULING:
            allowed_blocks=self.pcd.liTime.curselection()
            siteconfig['BlockConfig']['AllowedTime'] = []
            for allowed_time in allowed_blocks:
                siteconfig['BlockConfig']['AllowedTime'].append(allowed_time) # 24hr time stored

        siteconfig['Deterrents'] = {}
        siteconfig['Deterrents']['Method'] = self.pcd.intDetType.get()
        if self.pcd.intDetType.get() == DET_TYPE_ROLES:
            rowindex = self.pcd.lbRoleModels.curselection()
            if len(rowindex) != 1:
                showerror("Must select role model", "You must select a role model")
                return
            siteconfig['Deterrents']['RoleModelName'] = self.myRolesList[int(rowindex[0])]['Name']

        print siteconfig

        # Handle edit: check if it already exists in list. If so, replace it 
        found = 0
        for i in range(0, len(self.mySites)):
            if self.mySites[i]['url'] == siteconfig['url']:
                found = 1
                self.mySites[i] = siteconfig
                break

        if not found:
            self.mySites.append(siteconfig)
            self.pcd.lbSiteList.insert(END, siteconfig['url'])

        self.pcd.clearAllFields()

    """ Called when user clicks "Commit Changes" from project config dialog
    Saves config file to filename specified in the "Project Name" field """
    def saveFile(self): 
	fileName = self.pcd.eProjName.get()
	if len(fileName) > 1:
            outfile = open(PROJECT_DIR + fileName, 'wb')
            pickle.dump(self.mySites, outfile)
            outfile.close()      	
            self.getProjects()

    """ Called when user clicks "Edit" from main project list menu
    Open ProjectConfigDialog with values populated """
    def dEditProj(self):
		self.mySites = []
		self.pcd = ProjectConfigDialog(self)
		self.openProject()

    """ Called when user clicks "Add" from main project list menu"""
    def dNewProj(self):
		self.mySites = []
		self.pcd = ProjectConfigDialog(self)
	
    """ Called when user clicks "Delete" from main project list menu"""
    def dDeleteProj(self):
	selectedindex = self.lbProjects.curselection()
        if len(selectedindex) == 1:
            if askyesno("Delete Project?", "Are you sure you want to delete this project?"):
                filename = self.projectsList[int(selectedindex[0])]
                os.remove(PROJECT_DIR+filename)
                self.getProjects()
        else:
            showinfo("No project selected", "You must select a project before deleting")

    """ Called when user clicks "Employ" from the main project list menu"""
    def dEmployProj(self):
	selectedindex = self.lbProjects.curselection()
        if len(selectedindex) == 1:
            if askyesno("Employ Project?", "Are you sure you want to begin filtering content?"):
                filename = self.projectsList[int(selectedindex[0])]
                self.web_server_process = Popen(['sudo', 'python', '../filter/web_server.py', PROJECT_DIR+filename])
	
    """ Called when user clicks "Terminate" from main project list menu"""
    def terminate_project(self):
        if (self.web_server_process != None):
            if askyesno("Quit?", "Are you sure you want to quit? You must restart your computer"):
                showinfo("Project Terminated", "Your computer will now restart")
        else:
            showinfo("Filter not active", "The filter is not currently active")

    """ Create main window with list of previously configured projects"""
    def projectWindow(self):

	self.projectsWindow = Tk()
	self.projectsWindow.title("Pineapple!")
	
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
        bProjectsT=Button(frame, text="Terminate", command=self.terminate_project)
	bProjectsE.grid(row=0,column=0)
	bProjectsN.grid(row=0,column=1)
	bProjectsD.grid(row=0,column=2)
	bProjectsEm.grid(row=0,column=3)
        bProjectsT.grid(row=0, column=4)
	frame.grid(row=5,column=0)
	
	self.getProjects()
	
	mainloop()

    """ Called when user chooses to edit an existing project. The project window is created then 
    open_project is called to populate the form fields"""
    def openProject(self):
	pjname=self.projectsList[int(self.lbProjects.curselection()[0])]
        try:
            infile = open(PROJECT_DIR+pjname)
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
        except:
            showerror("Error opening project configuration", "Unable to open project configuration file")

    """ Populates list of previously configured projects to be listed in main window  """
    def getProjects(self):
	self.projectsList=[]
	self.lbProjects.delete(0,END)
        if os.path.exists(PROJECT_DIR):
            pro=os.listdir(PROJECT_DIR)
            for i in pro:
                self.projectsList.append(i)
                self.lbProjects.insert(END, i)
        else:
            os.makedirs(PROJECT_DIR)

		
def main():
    pj = ProjectConfig()

if __name__ == "__main__":
	main()

