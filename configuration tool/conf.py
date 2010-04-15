# File: hello2.py


from Tkinter import *
import tkFileDialog
import os

mySites=[]
liTime=0
intListType =0
entSite=2
lbSiteList=2
rbRadios=[]
picRole=0

def removeSite ():
		
	site=entSite.get()
	oldSites=lbSiteList.curselection()
	for i in oldSites:
		lbSiteList.delete(i)
		del mySites[int(i)]
		
	
	
	
def addSite ():
		
	site=entSite.get()
	print site
	mySites.append(site)
	lbSiteList.delete(0,END)
	for item in mySites:
		lbSiteList.insert(END,item)
	

def openFile():
	file=tkFileDialog.askopenfile(parent=root,mode='rb',title='Choose a file')
	if file!=None:
		info=file.readlines()
		
		newTime=[]
		newListType=IntVar()
		newWebs=[]
		section=0
		print info
		for j in info:
			i=str(j).rstrip()
			if i== "#":
				section+=1
			elif section==0:
				newTime.append(int(i))
			elif section==1:
				newListType.set(int(i))
			elif section==2:
				newWebs.append(i)
	
		print newTime
		print newListType.get()
		print newWebs
		
		
		liTime.selection_clear(0,END)
		for i in newTime:
			liTime.select_set(i)
		intListType=newListType
		
		rbRadios[intListType.get()-1].select()
			
		mySites=[]
		lbSiteList.delete(0,END)
		for i in newWebs:
			mySites.append(i)
			lbSiteList.insert(END,i)
		
			
			
		
	else:
		print "error"
		
		
def saveFile():
	fileName = tkFileDialog.asksaveasfilename(parent=root ,title="Save the image as...")
	if len(fileName ) > 0:
		file=open(fileName, 'w')
		li=liTime.curselection()
		for i in li:
			file.write(i+'\n')
		file.write("#\n")
		file.write(str(intListType.get())+'\n')
		file.write("#\n")
		for i in mySites:
			file.write(i+'\n')
			
	else:
		print "error"

		
def loadRoleModel():
	fileM=tkFileDialog.askopenfile(parent=root,mode='rb',title='Choose a file')
	if fileM!=None:
		picRole.config(file=fileM)
		
	else:
		print "error"
		
root= Tk()

#app=Websites(root)


#creating the website list
frame = Frame(root)
frame.grid(row=1,column=0)
entSite = Entry(frame)
entSite.grid(row=0, column=1)
laSite = Label(frame, text="Address")
laSite.grid(row=0,column=0)

bSite = Button(frame, text="Add Site", command=addSite)
bSite.grid(row=0,column=2)
lbSiteList=Listbox(root,selectmode=EXTENDED)
lbSiteList.grid(row=2, column=0)
bRemoveSite = Button(root, text="Remove Site", command=removeSite)
bRemoveSite.grid(row=3,column=0)




menubar = Menu(root)



# create a pulldown menu, and add it to the menu bar
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Open", command=openFile)
filemenu.add_command(label="Save", command=saveFile)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=filemenu)



helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="About")
menubar.add_cascade(label="Help", menu=helpmenu)

# display the menu
root.config(menu=menubar)



laWeb= Label(root, text="Websites")
laWeb.grid(row=0, column=0)
#txt = Text(root).grid(row=2, column=0, padx=20, pady=5)



intListType= IntVar()
fRadios=Frame(root)
rbRadios.append(Radiobutton(fRadios,text="Whitelist", variable=intListType,value=1))
rbRadios.append(Radiobutton(fRadios,text="Blacklist", variable=intListType,value=2))
rbRadios[0].grid(row=0, column=0)
rbRadios[1].grid(row=0, column=1)
fRadios.grid(row=5,column=0)



lTimeSection=Label(root, text="Time")
lTimeSection.grid(row=0, column=4)


fTimeList=Frame(root)

intTimeType=IntVar()
rbTimeRadios = []
rbTimeRadios.append(Radiobutton(fTimeList,text="Deny Always", variable=intTimeType,value=1))
rbTimeRadios.append(Radiobutton(fTimeList,text="Allow Breaks", variable=intTimeType,value=2))
rbTimeRadios.append(Radiobutton(fTimeList,text="Block Scheduling", variable=intTimeType,value=3))
rbTimeRadios[0].grid(row=0,column=0, sticky=W)

rbTimeRadios[1].grid(row=1,column=0,sticky=W)
fBreakFrame=Frame(fTimeList)
lbBreakLength=Label(fBreakFrame,text="Break Length")
lbBreakLength.grid(row=2,column=0,sticky=E,padx=2)
entBreakLength=Entry(fBreakFrame)
entBreakLength.grid(row=2,column=1)
fBreakFrame.grid(row=2,column=0,sticky=E,padx=20)

rbTimeRadios[2].grid(row=3,column=0,sticky=W)


fTimeScroll=Frame(fTimeList)
scTime = Scrollbar(fTimeScroll, orient=VERTICAL)
liTime = Listbox(fTimeScroll, selectmode=EXTENDED,yscrollcommand=scTime.set)

scTime.config(command=liTime.yview)
scTime.grid(row=0, column=1, rowspan=1, sticky=N+S)

for item in ["12 am", "1 am", "2 am", "3 am", "4 am", "5 am", "6 am",
	"7 am", "8 am", "9 am", "10 am", "11 am", "12 pm", "1 pm", "2 pm",
	"3 pm", "4  pm", "5 pm", "6 pm", "7 pm", "8 pm", "9 pm", "10 pm", 
	"11 pm"]:
	liTime.insert(END, item)
	
liTime.grid(row=0, column=0, sticky=N+S, rowspan=1)

fTimeScroll.grid(row=4,column=0)

fTimeList.grid(row=2, column=4, padx=15)


"""
fDeterance=Frame(root)
lbDeteranceLable=Label(fDeterance,text="Deterance")
cbTypeOut=Checkbutton(fDeterance,text="Typing")
cbTypeOut.grid(row=1, column=0)
cbRoleModel=Checkbutton(fDeterance,text="Rolemodel")
cbRoleModel.grid(row=2, column=0)
bLoadRole=Button(fDeterance, text="Load Image", command=loadRoleModel)


image1=PhotoImage(file="earth.gif")
panel=Label(fDeterance, image=image1)
panel.grid(row=5,column=5)

fDeterance.grid(row=0, column=4)
"""

	
mainloop()
