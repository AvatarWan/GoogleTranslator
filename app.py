from tkinter import Button,Checkbutton,Label,Tk,DoubleVar,IntVar,Scale,HORIZONTAL
import tkinter.font as tkFont
from tkinter import scrolledtext, INSERT,END, E,W,N,S

import time
import threading
import pyperclip

import psutil

from googletrans import Translator
translator = Translator()

# log = open("app.log", "a")
# import sys
# sys.stdout = log

def temp_trans(text):
	return "Translated "+text

class TranslateThread(threading.Thread):
	def __init__(self,callback,error_callback,text):
		super(TranslateThread,self).__init__()
		self._callback=callback
		self._error_callback=error_callback
		self._stopping=False
		self._text=text

	def run(self):
		# self._tr=temp_trans(self._text)
		# self._callback(self,self._tr)
		try:
			if self._stopping:
				self._error_callback(self)
			temp = translator.translate(self._text)
			self._tr = temp.text
			if not self._stopping:
				self._callback(self,self._tr)
			else:
				self._error_callback(self)
		except Exception as e:
			print(e)
			self._error_callback(self)

	def stop(self):
		self._stopping=True


def is_not_empty(text):
    if text is not "":
        return True
    return False

def print_to_stdout(clipboard_content):
    print ("Found url: %s" % str(clipboard_content))

class ClipboardWatcher(threading.Thread):
    def __init__(self, predicate, callback, pause=5.):
        super(ClipboardWatcher, self).__init__()
        self._predicate = predicate
        self._callback = callback
        self._pause = pause
        self._stopping = False

    def run(self):
        recent_value = ""
        while not self._stopping:
            tmp_value = pyperclip.paste()
            if tmp_value != recent_value:
                recent_value = tmp_value
                if self._predicate(recent_value):
                    self._callback(recent_value)
            time.sleep(self._pause)

    def stop(self):
        self._stopping = True

class CPUWatcher(threading.Thread):
	def __init__(self, callback, pause=5.):
		super(CPUWatcher, self).__init__()
		self._callback=callback
		self._pause=pause
		self._stopping=False

	def run(self):
		while not self._stopping:
			try:
				self._callback( str(psutil.Process().cpu_percent()) )
				time.sleep(self._pause)
			except Exception as e:
				print(e)
				print("Some Error!")

	def stop(self):
		self._stopping = True

class App:
    def __init__(self, root):
        self.root = root
        root.title("Google Translator")
        width=800
        height=130
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=True, height=True)

        GButton=Button(root)
        GButton["anchor"] = "center"
        GButton["bg"] = "#efefef"
        ft = tkFont.Font(family='Times',size=10)
        GButton["font"] = ft
        GButton["fg"] = "#000000"
        GButton["justify"] = "center"
        GButton["text"] = "Google Translate"
        GButton.grid(row=0, column=0,sticky=W+E+N+S)
        GButton["command"] = self.GButton_command

        self.top_screen = IntVar()
        GCheck=Checkbutton(root,variable=self.top_screen)
        GCheck["anchor"] = "center"
        ft = tkFont.Font(family='Times',size=10)
        GCheck["font"] = ft
        GCheck["fg"] = "#333333"
        GCheck["justify"] = "left"
        GCheck["text"] = " Top"
        GCheck.grid(row=0, column=1,sticky=W+N)
        GCheck["offvalue"] = "0"
        GCheck["onvalue"] = "1"
        GCheck["command"] = self.GCheck_command

        self.full_screen = IntVar()
        GFull = Checkbutton(root,variable=self.full_screen,fg="#333333",justify="left",text="Title Bar",command=self.GFull_command)
        GFull["font"]=ft
        GFull.select()
        GFull.grid(row=0,column=2,sticky=W+N)

        self.TSize = IntVar()
        self.TSlide = Scale(root,variable=self.TSize,from_=10,to=16,orient=HORIZONTAL,resolution=3,sliderlength=40,width=18,showvalue=0,command=self.TSlide_command)
        # ft2 = tkFont.Font(family='Times',size=8)
        # self.TSlide["font"]=ft2
        self.TSlide.grid(row=0,column=3,sticky=W+N)

        self.trans = DoubleVar()
        self.GSlide = Scale(root,variable=self.trans,from_=10,to=100,orient=HORIZONTAL,width=12,sliderlength=20,showvalue=0,resolution=5,cursor="sb_h_double_arrow",command=self.GSlide_command)
        self.GSlide.grid(row=1,column=0,columnspan=6,sticky=E+S+N+W)
        self.GSlide.set(100)

        self.Otext = ""
        self.GTextO=scrolledtext.ScrolledText(root,width=18, height=5)
        self.GTextO["borderwidth"] = 2
        self.GTextO["relief"] = "sunken"
        ft = tkFont.Font(family='Times',size=10)
        self.GTextO["font"] = ft
        self.GTextO["fg"] = "#333333"
        self.GTextO.insert(INSERT, "Original Text comes here!")
        self.GTextO.grid(row=2, column=0, columnspan=1,sticky=W+N+S+E)

        self.GTextT=scrolledtext.ScrolledText(root, width=90, height=5)
        self.GTextT["borderwidth"] = 2
        self.GTextT["relief"] = "sunken"
        ft = tkFont.Font(family='Times',size=10)
        self.GTextT["font"] = ft
        self.GTextT["fg"] = "#333333"
        self.GTextT.insert(INSERT, "Translated Text comes here!")
        self.GTextT.grid(row=2, column=1, columnspan=5,sticky=E+S+N+W)

        self.GStatus=Label(root)
        self.GStatus["anchor"] = "w"
        ft = tkFont.Font(family='Times',size=10)
        self.GStatus["font"] = ft
        self.GStatus["fg"] = "#333333"
        self.GStatus["justify"] = "left"
        self.GStatus["text"] = "Online"
        self.GStatus.grid(row=3, column=0,sticky=S+W)

        self.cpu_watcher = CPUWatcher(self.Cpu_command,1.)
        self.GCpu=Label(root)
        self.GCpu["anchor"] = "e"
        self.GCpu["justify"] = "right"
        self.GCpu["text"] = "_"
        self.GCpu.grid(row=3, column=5,sticky=E+S+N+W)
        self.cpu_watcher.start()

        root.grid_columnconfigure(0,weight=1)
        root.grid_columnconfigure(1,weight=1)
        root.grid_columnconfigure(2,weight=1)
        root.grid_columnconfigure(3,weight=1)
        root.grid_columnconfigure(4,weight=1)
        root.grid_columnconfigure(5,weight=1)
        root.grid_rowconfigure(0,weight=0)
        root.grid_rowconfigure(1,weight=0)
        root.grid_rowconfigure(2,weight=1)
        root.grid_rowconfigure(3,weight=0)

        root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
    	self.cpu_watcher.stop()
    	self.root.destroy()

    def __del__(self):
    	self.cpu_watcher.stop()

    def clipboard_command(self,Otext):
        self.Otext = Otext
        self.GTextO.delete('1.0', END) 
        self.GTextO.insert(END, Otext)
        self.Translate_command()

    def GButton_command(self):
    	self.Translate_command()

    def Translate_command(self):
    	print("async call for translation of self.Otext")
    	self.GStatus.config(text = "In Progress...")
    	self.translator_thread = TranslateThread(self.returned_text,self.returened_error,self.Otext)
    	self.translator_thread.start()

    # return from google translate succse
    def returned_text(self,caller,text):
    	if caller is self.translator_thread:
    		print("async finish")
    		self.GTextT.delete('1.0', END) 
    		self.GTextT.insert(END, text)
    		self.GStatus.config(text = "Online")

    # return from google translate error
    def returened_error(self,caller):
    	if caller is self.translator_thread:
    		print("async error")
    		self.GStatus.config(text="Retry Later")

    def Cpu_command(self,usage):
    	# print("usage : "+usage)
    	self.GCpu.config(text = str(psutil.Process().cpu_percent(interval=1)) + "%")

    def GCheck_command(self):
        if self.top_screen.get()==1:
            self.root.attributes('-topmost', 'true')
        else:
            self.root.attributes('-topmost', 'false')

    def GFull_command(self):
    	# Full
    	if self.full_screen.get()==0:
    		self.root.overrideredirect(True)
    		self.GSlide.grid_remove()
    	else:
    		self.root.overrideredirect(False)
    		self.GSlide.grid()
    	# if self.full_screen.get()==0:
    	# 	self.root.wm_attributes('-type', 'dock')
    	# else:
    	# 	self.root.wm_attributes('-type', 'splash')

    def GSlide_command(self,_):
        # print("slide" + str(self.trans.get()))
        self.root.attributes('-alpha', self.trans.get()/100)

    def TSlide_command(self,_):
    	ft = tkFont.Font(family='Times',size=self.TSize.get())
    	self.GTextT["font"]=ft

if __name__ == "__main__":
    root = Tk()
    app = App(root)
    watcher = ClipboardWatcher(is_not_empty, app.clipboard_command,0.2)
    watcher.start()
    root.mainloop()
    watcher.stop()

