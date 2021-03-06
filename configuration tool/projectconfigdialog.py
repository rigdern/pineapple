""" projectconfigdialog

ProjectConfigDialog Class - GUI implementation

Elements of this class are referenced in ProjectConfig

"""


from Tkinter import *
from constants import *

import tkMessageBox
import tkFileDialog
import os
import pickle
import shutil
from  tkMessageBox import *
from PIL import Image, ImageTk


class ProjectConfigDialog():
    def __init__(self, projconfig):
        self.projectconfig = projconfig
        self.lastselection = None
        self.build_layout()

    def remove_site(self):
        """ Called when user clicks "Remove Site." Deletes site from the list. """
        site = self.SiteStr.get()
        oldSites = self.lbSiteList.curselection()
        for i in oldSites:
            if self.projectconfig.mySites[int(i)]['url'] == site:
                self.lbSiteList.delete(i)
                del self.projectconfig.mySites[int(i)]
        self.look_for_site_field_edit(0)

    def load_role_model_list(self):
        """ Called once the project config dialog is created at the end of build_layout().
        Populates the list of role models from the file"""
        self.projectconfig.myRolesList = []
        self.lbRoleModels.delete(0, END)
        if os.path.isfile(ROLE_FILE_NAME):
            roleConfigFile = open(ROLE_FILE_NAME, 'r')
            if roleConfigFile != None:
                self.projectconfig.myRolesList = pickle.load(roleConfigFile)
                for role in self.projectconfig.myRolesList:
                    self.lbRoleModels.insert(END, role['Name'])

    def load_role_model_picture(self):
        """ Called when user clicks "Load Picture" from role model window. Prompts user for file
        of image and saves it for future use when saving"""
        self.imageFile = tkFileDialog.askopenfilename(parent=self.setting, title='Choose a file')
        if self.imageFile != None:
            shutil.copy(self.imageFile, PICS_DIR)

            self.imageFile = os.getcwd() + '/' + PICS_DIR + os.path.basename(self.imageFile)
            myPic = ImageTk.PhotoImage(Image.open(self.imageFile))
            self.lbRolePrev.config(image=myPic)
            self.lbRolePrev.image = myPic
            self.top.focus_set()

    def remove_role_model(self):
        """ Called when user selects "Remove" under role model list. Removes role model from listing"""
        selection = self.lbRoleModels.curselection()
        if len(selection) != 1:
            return

        selectedIndex = int(selection[0])
        self.lbRoleModels.delete(selectedIndex)
        self.projectconfig.myRolesList.pop(selectedIndex)
        self.save_role_model_list()

    def clear_all_fields(self):
        """ Clears all form elements. Done after adding a site when user should no longer
        see previous values"""
        self.intDetType.set(0)
        self.intTimeType.set(0)
        self.BreakLengthStr.set('')
        self.WaitTimeStr.set('')
        self.liTime.select_clear(0, END)
        self.lbRoleModels.selection_clear(0, END)
        self.look_for_site_field_edit(0)

    def edit_role_model_window(self):
        """ Called when user wants to edit a previously configured role model. Sets member variables
        relating to information about this role model then calls role_model_window(). This function 
        populate the window fields with these values."""
        selectedIndices = self.lbRoleModels.curselection()
        if len(selectedIndices) != 1:
            return

        roleModel = self.projectconfig.myRolesList[int(selectedIndices[0])]
        self.imageName = roleModel['Name']
        self.imageText = roleModel['QuotesList']
        self.imageFile = roleModel['ImagePath']
        self.role_model_window()

    def poll(self):
        """ Checks every 200ms to see if the site field has changed. This is used to implement the
        'edit site' function. When the site field is a site already listed, the add site button changes
        to 'edit site.' If they start changing the field after this, we want to change the button back
        to saying "add site." """
        currentselection = self.lbSiteList.curselection()
        if currentselection != self.lastselection or self.clickwaiting:
            self.lastselection = currentselection
            self.list_selection_changed(currentselection)
            self.set_click_waiting(0)
        self.lbSiteList.after(200, self.poll)
        
    def set_click_waiting(self, num):
        """ Used to help with 'edit site' functionality. Called when user clicks in site listbox. """
        self.clickwaiting = num


    def look_for_site_field_edit(self, setnow):
        """ When the user clicks on a site, we call this to change the button to say 'edit site'
        When the field changes after that, we check if this still makes sense. If not, we switch
        back to "add site" """
        if setnow:
            for site in self.projectconfig.mySites:
                if self.SiteStr.get() == site['url']:
                    self.bSite.config(text="Edit Site")
                    return

        self.bSite.config(text="Add Site")

    def list_selection_changed(self, selection):
        """ When the user clicks on a value in the site list, we should populate the form values
        with those related to this site policy"""
        if len(selection) < 1:
            return
        self.BreakLengthStr.set('')
        self.WaitTimeStr.set('')
        configobj = self.projectconfig.mySites[int(selection[0])]
        self.liTime.select_clear(0, END)
        self.SiteStr.set(configobj['url'])

        # Set block config piece of site policy
        blockmethod = configobj['BlockConfig']['Method']
        self.rbTimeRadios[blockmethod].select()
        if (blockmethod == TIME_TYPE_ALLOW_BREAKS):
            self.BreakLengthStr.set(str(configobj['BlockConfig']['BreakLength']))
            self.WaitTimeStr.set(str(configobj['BlockConfig']['TimeBetweenBreaks']))
        elif (blockmethod == TIME_TYPE_BLOCK_SCHEDULING):
            breaks = configobj['BlockConfig']['AllowedTime']
            for allowedtime in breaks:
                self.liTime.selection_set(allowedtime)

        # Set deterrent piece of site policy
        deterrentmethod = configobj['Deterrents']['Method']
        self.intDetType.set(deterrentmethod)
        self.lbRoleModels.select_clear(0, END)
        if deterrentmethod == DET_TYPE_ROLES:
            roleName = configobj['Deterrents']['RoleModelName']
            for i in range(0, len(self.projectconfig.myRolesList)):
                if self.projectconfig.myRolesList[i]['Name'] == roleName:
                    self.lbRoleModels.selection_set(i)
        self.look_for_site_field_edit(1)

    def save_role_model_list(self):
        """ Save the current list of role models and their corresponding configurations
        to the disk for future use"""
        fileOpen = open(ROLE_FILE_NAME, 'wb')
        if fileOpen != None:
            pickle.dump(self.projectconfig.myRolesList, fileOpen)
            fileOpen.close()

    def add_role_model_window(self):
        """ Open role model window. Because form fields are populated with imageText, imageFile, 
        and imageName members, clear these first"""
        self.imageText = []
        self.imageFile = ""
        self.imageName = ""
        self.role_model_window()

    def save_role_model(self):
        """ Called when committing a role model. Save the configuration internally and make
        entry in list if it's not already there"""
        if askyesno("Commit changes?", "Are you sure you want to commit changes to this role model?"):
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
                
            self.save_role_model_list()
            self.top.destroy()

    def role_model_window(self):
        """ Mostly gui implementation of role model window. We populate the name, text, and picture
        if this is an edit -- in that case the 3 corresponding members are set to non blank values"""
        self.top = Toplevel(self.setting)

        lbRoleMo = Label(self.top, text="Role Model")
        lbRoleMo.grid(row=0, column=1)

        fRoleName = Frame(self.top)
        lbRoleName = Label(fRoleName, text="Name")
        lbRoleName.grid(row=0, column=0)
        self.eRoleName = Entry(fRoleName)
        self.eRoleName.grid(row=0, column=1)
        self.eRoleName.insert(END, self.imageName)
        fRoleName.grid(row=1, column=0, sticky=W)

        lbPreview = Label(self.top, text="Preview")
        lbPreview.grid(row=2, column=0, sticky=W)

        self.lbRolePrev = Label(self.top)
        self.lbRolePrev.grid(row=2, column=0, sticky=W)

        try:
            if self.imageFile != "":
                imageLab = ImageTk.PhotoImage(Image.open(self.imageFile))
                self.lbRolePrev.config(image=imageLab)
                self.lbRolePrev.image = imageLab
        except:
            showerror("Error loading image", "Could not load the image: " + self.imageFile)

        bSetPicture = Button(self.top, text="Select Picture", command=self.load_role_model_picture)
        bSetPicture.grid(row=4, column=2)

        lbQuotes = Label(self.top, text="Quotes")
        lbQuotes.grid(row=4, column=0, sticky=W)
        self.tbQuotes = Text(self.top)
        self.tbQuotes.grid(row=5, column=0)

        for i in self.imageText:
            j = i + "\n"
            self.tbQuotes.insert(END, j)

        but = Button(self.top, text="commit", command=self.save_role_model)
        but.grid(row=6, column=0)

    def build_layout(self):
        """ GUI implementation of the main project config dialog"""
        self.setting = Toplevel(self.projectconfig.projects_dialog)
        menubar = Menu(self.setting)

        # create a pulldown menu, and add it to the menu bar
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_separator()

        # Placeholder for Help menu
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=lambda: showinfo("Pineapple!", "Pineapple is a filtering program for\n people with short attention spans"))
        menubar.add_cascade(label="Help", menu=helpmenu)

        # display the menu
        self.setting.config(menu=menubar)

        # create the website list
        fWebsites = Frame(self.setting)
        frame = Frame(fWebsites)
        frame.grid(row=2, column=0)

        laWeb = Label(fWebsites, text="Websites")
        laWeb.grid(row=0, column=0)

        self.clickwaiting = 0

        self.SiteStr = StringVar()
        entSite = Entry(frame, textvariable=self.SiteStr)
        entSite.grid(row=0, column=1)
        entSite.bind('<Key>', lambda e: self.look_for_site_field_edit(0))

        laSite = Label(frame, text="Address")
        laSite.grid(row=0, column=0)

        self.bSite = Button(frame, text="Add Site", command=self.projectconfig.add_site)
        self.bSite.grid(row=0, column=2)

        self.lbSiteList = Listbox(fWebsites, selectmode=EXTENDED, exportselection=0)
        self.lbSiteList.grid(row=3, column=0)
        self.lbSiteList.bind('<Button-1>', lambda e: self.set_click_waiting(1))

        bRemoveSite = Button(fWebsites, text="Remove Site", command=self.remove_site)
        bRemoveSite.grid(row=4, column=0)

        self.poll()  # Wait for user to click on site in list -- populate right side accordingly

        # Blacklist / Whitelist
        self.intListType = IntVar(value=1)

        fWebsites.grid(row=3, column=0)

        # Blocking Method
        fBlock = Frame(self.setting)
        lTimeSection = Label(fBlock, text="Blocking Method")
        lTimeSection.grid(row=1, column=4)

        fTimeList = Frame(fBlock)
        fTimeList.grid(row=3, column=4, padx=15)

        self.intTimeType = IntVar()
        self.rbTimeRadios = []
        self.rbTimeRadios.append(Radiobutton(fTimeList, text="Deter Once", variable=self.intTimeType, value=TIME_TYPE_DENY_ALWAYS))
        self.rbTimeRadios.append(Radiobutton(fTimeList, text="Allow Breaks", variable=self.intTimeType, value=TIME_TYPE_ALLOW_BREAKS))
        self.rbTimeRadios.append(Radiobutton(fTimeList, text="Block Scheduling", variable=self.intTimeType, value=TIME_TYPE_BLOCK_SCHEDULING))
        self.rbTimeRadios[0].grid(row=0, column=0, sticky=W)
        self.rbTimeRadios[1].grid(row=1, column=0, sticky=W)
        self.rbTimeRadios[2].grid(row=4, column=0, sticky=W)

        # Blocking Method / Allow Breaks
        fBreakFrame = Frame(fTimeList)
        lbBreakLength = Label(fBreakFrame, text="Break Length")
        lbBreakLength.grid(row=2, column=0, sticky=E, padx=2)

        self.BreakLengthStr = StringVar()
        entBreakLength = Entry(fBreakFrame, textvariable=self.BreakLengthStr)
        entBreakLength.grid(row=2, column=1)

        lbWaitTime = Label(fBreakFrame, text="Time Between Breaks")
        lbWaitTime.grid(row=3, column=0, sticky=E, padx=2)

        self.WaitTimeStr = StringVar()
        entWaitTime = Entry(fBreakFrame, textvariable=self.WaitTimeStr)
        entWaitTime.grid(row=3, column=1)

        fBreakFrame.grid(row=3, column=0, sticky=E, padx=20)

        # Blocking Method / Block Scheduling
        fTimeScroll = Frame(fTimeList)
        fTimeScroll.grid(row=6, column=0)
        scTime = Scrollbar(fTimeScroll, orient=VERTICAL)
        self.liTime = Listbox(fTimeScroll, selectmode=EXTENDED, yscrollcommand=scTime.set, exportselection=0)
        self.liTime.grid(row=0, column=0, sticky=N + S, rowspan=1)

        scTime.config(command=self.liTime.yview)
        scTime.grid(row=0, column=1, rowspan=1, sticky=N + S)

        for item in ["12 am", "1 am", "2 am", "3 am", "4 am", "5 am", "6 am",
                     "7 am", "8 am", "9 am", "10 am", "11 am", "12 pm", "1 pm", "2 pm",
                     "3 pm", "4  pm", "5 pm", "6 pm", "7 pm", "8 pm", "9 pm", "10 pm",
                     "11 pm"]:
            self.liTime.insert(END, item)

        fBlock.grid(row=3, column=4)

        #Deterrents
        fDeterrents = Frame(self.setting)
        self.intDetType = IntVar()

        lbDet = Label(fDeterrents, text="Deterrents")
        lSpace = Label(fDeterrents, text="")
        lSpace.grid(row=0, column=0)
        lbDet.grid(row=1, column=6)
        fDets = Frame(fDeterrents)

        rbDetRadios = []
        rbDetRadios.append(Radiobutton(fDets, text="Only Block", variable=self.intDetType, value=DET_TYPE_DENY))
        rbDetRadios.append(Radiobutton(fDets, text="Type Deterrent", variable=self.intDetType, value=DET_TYPE_TYPE))
        rbDetRadios.append(Radiobutton(fDets, text="Explain Value", variable=self.intDetType, value=DET_TYPE_EXPLAIN))
        rbDetRadios.append(Radiobutton(fDets, text="Role Models", variable=self.intDetType, value=DET_TYPE_ROLES))

        rbDetRadios[0].grid(row=0, column=0, sticky=W)
        rbDetRadios[1].grid(row=1, column=0, sticky=W)
        rbDetRadios[2].grid(row=2, column=0, sticky=W)
        rbDetRadios[3].grid(row=3, column=0, sticky=W)

        self.lbRoleModels = Listbox(fDets, exportselection=0)
        self.lbRoleModels.grid(row=4, column=0)
        self.lbRoleModels.bind("<Double-Button-1>", lambda e: self.edit_role_model_window())

        roleFrame = Frame(fDets)
        bAddWindow = Button(roleFrame, text="Add New")
        bAddWindow.config(command=self.add_role_model_window)
        bAddWindow.grid(row=0, column=0)
        bEditWindow = Button(roleFrame, text="Edit Selection")
        bEditWindow.config(command=self.edit_role_model_window)
        bEditWindow.grid(row=0, column=1)
        bDelete = Button(roleFrame, text="Delete Role Model")
        bDelete.config(command=self.remove_role_model)
        bDelete.grid(row=0, column=2)

        roleFrame.grid(row=5, column=0)

        fDets.grid(row=3, column=6)
        fDeterrents.grid(row=3, column=6)

        self.load_role_model_list()

        fProjInfo = Frame(self.setting)
        lProjName = Label(fProjInfo, text="Project Name")
        self.eProjName = Entry(fProjInfo)
        bProjCommit = Button(fProjInfo, text="Commit Changes", command=self.projectconfig.save_project)
        lProjName.grid(row=0, column=0)
        self.eProjName.grid(row=0, column=1)
        bProjCommit.grid(row=0, column=2,)
        fProjInfo.grid(row=0, column=4)

        self.setting.title("Project Configuration")
