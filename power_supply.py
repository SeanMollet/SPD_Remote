#!/usr/bin/env python3

import pyvisa as visa
from time import sleep
import tkinter as tk
import tkinter.font as tkFont
import threading

class App:
    def __init__(self, root):
        self.runThread = True

        self.supplyIP = "10.23.0.25"
        
        self.ledFont = tkFont.Font(family='Seven Segment',size=40)
        self.gaugeFont = tkFont.Font(family='Times',size=20)
        
        root.title("Powersupply Control")
        self.gaugeUpdateFuncs = []
        #setting window size
        width=460
        height=500
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        self.voltage = 0.00
        self.voltageActual = 0.00
        self.currentLimit = 0.00
        self.currentActual = 0.00

        self.dataThread = threading.Thread(target=self.readPowerSupply)
        self.dataThread.start()

        #ledFont = pyglet.font.load("Seven Segment")
        
        xPos = 40
        yPos = 20

        gaugeLabel=tk.Label(root)
        gaugeLabel["font"] = self.gaugeFont
        gaugeLabel["fg"] = "#ffffff"
        gaugeLabel["justify"] = "center"
        gaugeLabel["text"] = "Selected"
        gaugeLabel.place(x=xPos,y=yPos,width=160,height=30)
        
        gaugeLabel=tk.Label(root)
        gaugeLabel["font"] = self.gaugeFont
        gaugeLabel["fg"] = "#ffffff"
        gaugeLabel["justify"] = "center"
        gaugeLabel["text"] = "Actual"
        gaugeLabel.place(x=xPos+200,y=yPos,width=160,height=30)

        yPos += 50

        self.addGauge(xPos,yPos,"Voltage", lambda : '{0:.3f}V'.format(self.voltage))
        self.addGauge(xPos,yPos+80,"Current", lambda : '{0:.3f}A'.format(self.currentLimit))

        self.addGauge(xPos+200,yPos,"Voltage", lambda : '{0:.3f}V'.format(self.voltageActual))
        self.addGauge(xPos+200,yPos+80,"Current", lambda : '{0:.3f}A'.format(self.currentActual))


        ft = tkFont.Font(family='Times',size=30)
        
        GButton_92=tk.Button(root)
        GButton_92["bg"] = "#e9e9ed"
        GButton_92["font"] = ft
        GButton_92["fg"] = "#00ff00"
        GButton_92["justify"] = "center"
        GButton_92["text"] = "On"
        GButton_92.place(x=20,y=290,width=200,height=200)
        GButton_92["command"] = self.onCmd

        GButton_93=tk.Button(root)
        GButton_93["bg"] = "#e9e9ed"
        GButton_93["font"] = ft
        GButton_93["fg"] = "#000000"
        GButton_93["justify"] = "center"
        GButton_93["text"] = "Off"
        GButton_93.place(x=240,y=290,width=200,height=200)
        GButton_93["command"] = self.offCmd

    def onCmd(self):
        print("Turning On")
        if self.power is not None:
            try:
                self.power.query('OUTPUT CH1,ON')
            except Exception:
                pass


    def offCmd(self):
        print("Turning Off")
        if self.power is not None:
            try:
                self.power.query('OUTPUT CH1,OFF')
            except Exception:
                pass

    def updateGauges(self):
        for gauge in self.gaugeUpdateFuncs:
            if gauge[0] is not None and gauge[1] is not None:
                gauge[0]["text"] = gauge[1]()

    def addGauge(self,x,y,name,getValue):

        gaugeLabel=tk.Label(root)

        gaugeLabel["font"] = self.gaugeFont
        gaugeLabel["fg"] = "#ffffff"
        gaugeLabel["justify"] = "center"
        gaugeLabel["text"] = name
        gaugeLabel.place(x=x,y=y+40,width=160,height=30)

        gaugeMeter=tk.Label(root)
        gaugeMeter["font"] = self.ledFont
        gaugeMeter["fg"] = "#00ff00"
        gaugeMeter["justify"] = "center"
        gaugeMeter["text"] = getValue()
        gaugeMeter.place(x=x,y=y,width=160,height=32)

        self.gaugeUpdateFuncs.append((gaugeMeter,getValue))

    def readPowerSupply(self):
        self.power = visa.ResourceManager("@py").open_resource("TCPIP::"+self.supplyIP+"::INSTR")
        self.device = self.power.query("*IDN?")
        if len(self.device)==0:
            print("No device found!")
            return
        
        print("Identified device:",self.device)
        
        while self.runThread:
            try:
                voltage = self.power.query('MEASure:VOLTage?')
                current = self.power.query('MEASure:CURRent?')
                voltageSelected = self.power.query('VOLTage?')
                currentLimit = self.power.query('Current?')

                self.voltageActual = float(voltage)
                self.currentActual = float(current)
                self.voltage = float(voltageSelected)
                self.currentLimit = float(currentLimit)
                self.updateGauges()

                #print("Voltage:",voltage,"Current:",current,"VS:",voltageSelected,"CL:",currentLimit)
            except Exception:
                pass
            sleep(.2)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()



