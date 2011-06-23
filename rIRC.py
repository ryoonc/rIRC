#! /usr/bin/env python
# $Author: ee364f08 $
# $Date: 2011-04-13 23:58:32 -0400 (Wed, 13 Apr 2011) $
# $HeadURL: svn+ssh://ece364sv@ecegrid-lnx/home/ecegrid/a/ece364sv/svn/S11/students/ee364f08/Lab12/eceIRC.py $
# $Revision: 23962 $

import irclib
import sys
import string
from Tkinter import *
import threading
import tkMessageBox
import tkFont

def spin():
    global done, irc
    while done == 0:
        irc.process_once(0.2)
    sys.exit(0)

def die():
    global done
    done = 1
    sys.exit(0)

def on_join(conn, event):
    global ChannelWindows
    window = ChannelWindows[event.target()]
    window.text.config(state=NORMAL)
    window.text.insert(END, "*** " + event.source() + " joined " + event.target() + "\n")
    window.text.config(state=DISABLED)
    window.text.yview(END)
    if server.get_nickname() != event.source().split("!")[0]:
        window.listNick.insert(END, event.source().split("!")[0])
    window.sort_list()

def on_part(conn, event):
    global ChannelWindows
    if server.get_nickname() != event.source().split("!")[0]:
        window = ChannelWindows[event.target()]
        window.text.config(state=NORMAL)
        window.text.insert(END, "*** " + event.source() + " left " + event.target() + "\n")
        window.text.config(state=DISABLED)
        window.text.yview(END)
    
        # deletes nickname from list when user parts
        temp_list = list(window.listNick.get(0, END))
        counter = 0
        for item in temp_list:
            if item == event.source().split("!")[0]:
                break
            counter = counter + 1
        window.listNick.delete(counter)

def on_quit(conn, event):
    global ChannelWindows
    # remove nickname from all channels
    for key, value in ChannelWindows.items():
        temp_list = list(value.listNick.get(0, END))
        # deletion iterate
        counter = 0
        for item in temp_list:
            name = event.source().split("!")[0]
            if item == event.source().split("!")[0]:
                value.listNick.delete(counter)
                # display that user quit
                value.text.config(state=NORMAL)
                value.text.insert(END, "*** " + event.source() + " quit IRC\n")
                value.text.config(state=DISABLED)
                break
            if item == "@" + event.source().split("!")[0]:
                value.listNick.delete(counter)
                # display that user quit
                value.text.config(state=NORMAL)
                value.text.insert(END, "*** @" + event.source() + " quit IRC\n")
                value.text.config(state=DISABLED)
                break

            counter = counter + 1
        
def on_pubmsg(conn, event):
    global ChannelWindows
    window = ChannelWindows[event.target()]
    nickname = event.source().split("!")
    window.text.config(state=NORMAL)
    window.text.insert(END, "<" + nickname[0] + "> " + event.arguments()[0] + "\n")
    window.text.config(state=DISABLED)
    window.text.yview(END)

def on_namreply(conn, event):
    global ChannelWindows
    window = ChannelWindows[event.arguments()[1]]
    for item in event.arguments()[2].split():
        window.listNick.insert(END, item)
    window.listNick.yview(END)
    window.sort_list()

def on_currenttopic(conn, event):
    global ChannelWindows
    window = ChannelWindows[event.arguments()[0]]
    window.title(event.arguments()[0] + " - " + event.arguments()[1])

def on_list(conn, event):
    global listWindow
    i = iter(event.arguments())
    listWindow.list.insert(END, i.next() + " " + i.next() \
            + " " + i.next())
    listWindow.list.yview(END)

# TODO: Expand
def on_liststart(conn, event):
    print "Inside liststart\n"
    print event.arguments()

# TODO: Expand
def on_listend(conn, event):
    print "INSIDE OF LIST END\n"
    print event.arguments()

# TODO: Expand
def on_privmsg(conn, event):
    global PrivWindows

    if event.source().split("!")[0] in PrivWindows:
        privWin = PrivWindows[event.source().split("!")[0]]
    else:
        PrivWindows[event.source().split("!")[0]] = PrivWindow(event.source().split("!")[0]) 
        privWin = PrivWindows[event.source().split("!")[0]]
    
    privWin.text.config(state=NORMAL)
    privWin.text.insert(END, "<" + event.source().split("!")[0] + "> " + event.arguments()[0] + "\n")
    privWin.text.config(state=DISABLED)
    privWin.text.yview(END)
    privWin.lift()


def shandler(conn,event):
    global SSwin
    SSwin.text.config(state=NORMAL)
    SSwin.text.insert(END, "*** " + string.join(event.arguments(), ' ') + "\n")
    SSwin.text.config(state=DISABLED)
    SSwin.text.yview(END)

class ListWindow( Toplevel ):
    def __init__(self):
        global listWindow
        Toplevel.__init__(self, background="white")
        self.grid()
        self.createWidgets()
        self.protocol("WM_DELETE_WINDOW", self.close_win)

    def createWidgets( self ):
        self.filterLabel = Label(self, text="Filter:")
        self.filterLabel.grid( column=0, columnspan=2, sticky=E )
        self.filterLabel.config(background="white")

        self.entry = Entry( self )
        self.entry.grid( row=0, column=2, columnspan=1, sticky=W+E )
        self.entry.select_range(0, END)
        self.entry.focus_set()
        self.bind('<Return>', self.enterFilter)
        self.entry.config(background="white", highlightbackground="black", \
                highlightthickness=0)

        # 1 if the button is selected, 0 if not
        self.checkFilter = IntVar()
        self.defaultCheck = Checkbutton( self, text="default filter", \
                variable=self.checkFilter, command=self.clickBox)
        self.defaultCheck.grid( row=0, column=3, columnspan=4, sticky=W )
        self.defaultCheck.config( activebackground="white", activeforeground="grey", \
                bg="white", highlightthickness=0 )

        self.list = Listbox( self, width=95, height=20 )
        self.list.grid( rowspan=2, columnspan=7, row=1, column=0, sticky=N+W+E+S )
        self.list.config(background="white", highlightbackground="black", \
                highlightthickness=0)
        self.list.bind("<Double-Button-1>", self.joinChannel)

        self.scrollbar = Scrollbar( self, command = self.list.yview )
        self.scrollbar.grid( rowspan=2, column=7, row = 1, sticky=N+S )
        self.scrollbar.config(troughcolor="grey", activebackground="grey", \
                    background="white", highlightbackground="black", \
                    highlightthickness=0)

        self.list.configure( yscrollcommand = self.scrollbar.set )

        #self.rowconfigure( 1, weight = 1 )
        #self.columnconfigure( 1, weight = 1 )

    # when checkbutton is clicked
    def clickBox( self ):
        # Regex: #ece(0?3[7-9]|0?[4-9][0-9]|[1-3][0-9][0-9]|4[0-3][0-7])([a-zA-Z]([a-zA-Z0-9])*)?
        print "entered clickBox\n"

    # when user presses enter for input
    def enterFilter( self, event ):
        print "entered enterFilter\n"

    # TODO: Expression for channel name will be invalid once regex is finished
    def joinChannel( self, event ):
        global ChannelWindows
        channelName = self.list.get(ACTIVE).split()[0]
        ChannelWindows[channelName] = ChannelWindow(channelName)

    # TODO: Decide whether or not to keep list info in memory or not
    def close_win ( self ):
        self.list.delete(0, END)
        self.withdraw()


class ServerStatus( Frame ):
    def __init__(self, master=None, background="black"):
        Frame.__init__(self, master)
        self.grid()
        self.createWidgets()

    def createWidgets( self ):
        global irc
        
        # Create Frame and Grid
        Frame.__init__( self )
        self.master.title( "Project Phase 1" )
        self.master.rowconfigure( 0, weight = 1 )
        self.master.columnconfigure( 0, weight = 1 )
        self.grid( sticky = W+E+N+S )
          
        # Create textbox
        self.text = Text( self, width = 125, height = 25 )
        self.text.grid( rowspan = 3, sticky = W+E+N+S )
        self.text.config(state=DISABLED, background="white", highlightbackground="black", \
                highlightthickness=0)

        # Create Entry
        self.entry = Entry( self )
        self.entry.grid( row = 3, columnspan = 2, sticky = W+E+N+S )
        self.entry.select_range(0,END)
        self.entry.focus_set()
        self.entry.bind('<Return>', self.entryBox) # Trigger on enter
        self.entry.config(background="white", highlightbackground="black", \
                highlightthickness=0)
        # Create scrollbar
        self.scrollbar = Scrollbar( command = self.text.yview )
        self.scrollbar.grid( row = 0, column = 1, sticky = N+S )
        self.scrollbar.config(troughcolor="grey", activebackground="grey", \
                background="white", highlightbackground="black", \
                highlightthickness=0)

        # Join Scrollbar w/ text box
        self.text.configure( yscrollcommand = self.scrollbar.set )

        self.rowconfigure( 1, weight = 1 )
        self.columnconfigure( 1, weight = 1 )

    # TODO: Change user input matching to regex or better method
    # TODO: Create raise() methods for all toplevel windows
    def entryBox ( self, event ):
        global SSwin, server, ChannelWindows, listWindow, PrivWindows
        com = SSwin.entry.get().split()
    
        if len(com) >= 2:
            if com[0] == "/join":
                ChannelWindows[com[1]]=ChannelWindow(com[1])
            elif com[0] == "/part":
                server.part(com[1])
            elif com[0] == "/list":
                if listWindow.state() == "withdrawn":
                    listWindow.deiconify()
                    server.list()
                else:
                    SSwin.text.config(state=NORMAL)
                    SSwin.text.insert(END, "* The channel list is already open\n")
                    SSwin.text.config(state=DISABLED)
                #ListWindow()
            elif com[0] == "/exit":
                if tkMessageBox.askokcancel("Quit?", "Are you sure you want to quit?"):
                    die() 
        else:
            SSwin.text.config(state=NORMAL)
            SSwin.text.insert(END, "* You are not on a channel\n" )
            SSwin.text.config(state=DISABLED)
        
        SSwin.entry.delete('0', END)
        SSwin.text.yview(END)
        SSwin.entry.focus_set()


class ChannelWindow( Toplevel ):
    def __init__(self, args):
        global server
        Toplevel.__init__(self)
        self.channel = args
        self.createWidgets()
        server.join(args)
        self.protocol("WM_DELETE_WINDOW", self.close_win)

    def createWidgets( self ):
        self.title(self.channel)

        #self.customFont = tkFont.Font(family="Helvetica", size=20)

        self.text = Text( self, width = 100, height=25)
        self.text.grid( row = 0, column = 1, sticky = N+W+S+E )
        self.text.config(state=DISABLED, background="white", highlightbackground="black", \
                highlightthickness=0)
        

        self.listNick = Listbox( self, width = 25, height = 25 )
        self.listNick.grid( row = 0, column = 3, sticky = N+W+E+S )
        self.listNick.config(background="white", highlightthickness=0, \
                highlightbackground="black")
        self.listNick.bind("<Double-Button-1>", self.privMsg)

        self.scrollbarText = Scrollbar(self, command = self.text.yview )
        self.scrollbarText.grid( row = 0, column = 2, sticky = N+S)
        self.scrollbarText.config(troughcolor="black", activebackground="white")
        self.scrollbarText.config(troughcolor="grey", activebackground="grey", \
                background="white", highlightbackground="black", \
                highlightthickness=0)


        self.scrollbarList = Scrollbar(self, command = self.listNick.yview )
        self.scrollbarList.grid( row = 0, column = 4, sticky = N+S)
        self.scrollbarList.config(troughcolor="grey", activebackground="grey", \
                background="white", highlightbackground="black", \
                highlightthickness=0)

        self.text.configure( yscrollcommand = self.scrollbarText.set )
        self.listNick.configure( yscrollcommand = self.scrollbarList.set )

        self.entry = Entry( self )
        self.entry.grid( row = 3, columnspan = 5, sticky = N+W+E+S )
        self.entry.config(background="white", highlightthickness=0, \
                highlightbackground="black")
        self.entry.bind('<Return>', self.channelEntryBox) # Trigger on enter

        self.entry.focus_set()

    # curselection() returns currently selected list index # (starting w/ 0)
    def privMsg( self, event ):
        global PrivWindows
        PrivWindows[self.listNick.get(ACTIVE)] = PrivWindow(self.listNick.get(ACTIVE))

    def sort_list( self ):
        #function to sort listbox items case insensitive
        self.temp_list = list(self.listNick.get(0, END))
        self.temp_list.sort(key=str.lower)
        self.listNick.delete(0, END)
        for item in self.temp_list:
            self.listNick.insert(END, item)

    def channelEntryBox ( self, event ):
        global server, ChannelWindows
        com = self.entry.get().split()
        if len(com) >= 1:
            if com[0] == "/join":
                ChannelWindows[com[1]]=ChannelWindow(com[1])
            elif com[0] == "/part":
                server.part(com[1])
            elif com[0] == "/exit":
                if tkMessageBox.askokcancel("Quit?", "Are you sure you want to quit?"):
                    die() 
            else:
                server.privmsg( self.channel, self.entry.get())
                self.text.config(state=NORMAL)
                self.text.insert(END, "<" + server.get_nickname() + "> " + self.entry.get() + "\n" )
                self.text.config(state=DISABLED)

        self.entry.delete('0', END)
        self.text.yview(END)
        self.entry.focus_set()

    def close_win ( self ):
        global server, ChannelWindows
        server.part(self.channel)
        self.channel, self = ChannelWindows.popitem()
        self.destroy()

class ConnectWindow( Frame ):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, background="white", *args, **kwargs)
        self.grid()
        self.createWidgets()
    
    def createWidgets( self ):
        # Create Frame and Grid
        self.master.title("Connection")
        self.grid( sticky = N+W+E+S )
        
        self.addressEntry = Entry ( self )
        self.addressEntry.grid( row = 1, column=2, columnspan = 3, sticky = N+W+E+S )
        self.addressEntry.config(background="white")

        self.addressEntry.insert(END, "ecegrid-lnx.ecn.purdue.edu:6667")

        self.nicknameEntry = Entry ( self )
        self.nicknameEntry.grid( row = 2, column=2, columnspan = 3, sticky = N+W+E+S )
        self.nicknameEntry.config(background="white")

        self.nicknameEntry.insert(END, "cykimTEST")

        self.namelbl = Label(self, text="Server Name:")
        self.namelbl.grid( row = 1 , column=1, sticky = N+W+E+S )
        self.namelbl.config(background="white") 

        self.nicklbl = Label(self, text="Nickname:")
        self.nicklbl.grid( row = 2, column=1, sticky = N+W+E+S )
        self.nicklbl.config(background="white") 

        self.button = Button(self, text="Connect!", command=self.quit)
        self.button.grid( row = 3, column=3, sticky = N+W+E+S )
        self.button.config(activebackground="grey", background="white")

        self.rowconfigure( 1, weight = 1 )
        self.columnconfigure( 1, weight = 1 )

        self.addressEntry.focus_set()

    def quit ( self ):
        global root, top, server, CONNwin
        try:
            address = CONNwin.addressEntry.get().split(":")
            server.connect(address[0], int(address[1]), CONNwin.nicknameEntry.get())
            root.deiconify()
            top.destroy()
        except irclib.ServerConnectionError:
            tkMessageBox.showinfo(title="Error", message="Connect Error!")

class PrivWindow( Toplevel ):
    def __init__(self, args):
        Toplevel.__init__(self)
        self.uid = args
        self.createWidgets()
        self.protocol("WM_DELETE_WINDOW", self.close_win)

    def createWidgets( self ):
        self.title(self.uid)
        #self.grid(sticky = N+W+E+S)

        self.text = Text(self, width = 95, height = 27)
        self.text.grid(row = 0, column = 0, sticky = N+W+S+E)
        self.text.config(state=DISABLED, background="white", highlightbackground="black", \
                highlightthickness=0)
        
        self.scrollbarText = Scrollbar(self, command = self.text.yview )
        self.scrollbarText.grid( row = 0, column = 1, sticky = N+S)
        self.scrollbarText.config(troughcolor="black", activebackground="white")
        self.scrollbarText.config(troughcolor="grey", activebackground="grey", \
                background="white", highlightbackground="black", \
                highlightthickness=0)

        self.text.configure( yscrollcommand = self.scrollbarText.set )

        self.entry = Entry( self )
        self.entry.grid( row = 1, columnspan = 2, sticky = N+W+E+S )
        self.entry.config(background="white", highlightthickness=0, \
                highlightbackground="black")
        self.entry.bind('<Return>', self.entryBox) # Trigger on enter

        self.entry.focus_set()

    def entryBox(self, event):
        print "entered entryBox\n"
        server.privmsg( self.uid, self.entry.get())
        self.text.config(state=NORMAL)
        self.text.insert(END, "<" + server.get_nickname() + "> " + self.entry.get() + "\n" )
        self.text.config(state=DISABLED)
        
        self.entry.delete('0', END)
        self.text.yview(END)
        self.entry.focus_set()

    def close_win ( self ):
        global server, PrivWindows
        self.uid, self = PrivWindows.popitem()
        self.destroy()


#######################################################

# Threading variable
done = 0

# Objects
irc = irclib.IRC()
server = irc.server()

root = Tk()
SSwin = ServerStatus(master=root)
root.withdraw()

top = Toplevel(bg="white")
CONNwin = ConnectWindow(master=top)

ChannelWindows = {}

listWindow = ListWindow()
listWindow.withdraw()

PrivWindows = {}

#PrivWindow("cykim")

# Phase 1
server.add_global_handler("currenttopic", on_currenttopic)
server.add_global_handler("namreply", on_namreply)
server.add_global_handler("pubmsg", on_pubmsg)
server.add_global_handler("join", on_join)
server.add_global_handler("part", on_part)
server.add_global_handler("quit", on_quit)
# Phase 2
server.add_global_handler("list", on_list)
server.add_global_handler("liststart", on_liststart)
server.add_global_handler("listend", on_listend)
server.add_global_handler("privmsg", on_privmsg)

# Server callbacks
server.add_global_handler("yourhost", shandler)
server.add_global_handler("created", shandler)
server.add_global_handler("myinfo", shandler)
server.add_global_handler("featurelist", shandler)
server.add_global_handler("luserclient", shandler)
server.add_global_handler("luserop", shandler)
server.add_global_handler("luserchannels", shandler)
server.add_global_handler("luserme", shandler)
server.add_global_handler("n_local", shandler)
server.add_global_handler("n_global", shandler)
server.add_global_handler("luserconns", shandler)
server.add_global_handler("luserunknown", shandler)
server.add_global_handler("welcome", shandler)
server.add_global_handler("motd", shandler)

# Start irc threading
thread1 = threading.Thread(target=spin)
thread1.start()

root.mainloop()
die()
