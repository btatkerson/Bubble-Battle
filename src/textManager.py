import src.app

from PyQt4 import QtCore, QtGui
from src.timer import timer
from src.timerManager import timerManager
import re

app = src.app.app

ALIGN_CENTER='CENTER'
ALIGN_RIGHT='RIGHT'
ALIGN_LEFT='LEFT'
BOLD='BOLD'
ITALIC='ITALIC'
UNDERLINE='UNDERLINE'
STRIKETHROUGH='STRIKETHROUGH'
SUBSCRIPT='SUBSCRIPT'
SUPERSCRIPT='SUPERSCRIPT'

'''
Can find any number in a given string

re.findall('[0-9]*[.]?[0-9]*[0-9.]','54.14 68.1 .023 23 32.')
'''

class textManager(QtGui.QGraphicsTextItem):
    def __init__(self, text_width=None, time_delay=None, offset=(0,0), parent=None, scene=None):
        QtGui.QGraphicsTextItem.__init__(self, parent=parent, scene=scene)
        self.timeMng=timerManager()
        self.timeMng.setTimer('delay',time_delay,1)

        self.__inactive=True
        self.__timer_delay=time_delay

        self.__header = ""
        self.__footer = ""

        self.__offset = offset

        self.__default_face = None
        self.__default_color = None
        self.__default_size = None
        self.__default_alignment = None
        self.__default_bold = None
        self.__default_italic = None
        self.__default_underline = None
        self.__default_strikethrough  = None

        self.__static_text=""
        self.__var_update=True
        self.__var_text=""

        self.__textLine_Update = True
        
        if isinstance(text_width, (int, float)):
            self.setTextWidth(text_width)

        if isinstance(offset,(tuple, list)):
            if len(offset)==2:
                self.setPos(QtCore.QPointF(offset[0],offset[1]))
                    
        
        self.__vars={}
        self.__lines={}

    def deactivateTextManager(self):
        self.__inactive = True
        return self.__inactive

    def activateTextManager(self):
        self.__inactive = False
        return self.__inactive

    def isTextManagerDeactivated(self):
        return self.__inactive
        
    def isTextManagerActivated(self):
        return not self.__inactive

    def setTimerDelay(self, delay_in_seconds):
        self.timeMng.setTimer('delay',delay_in_seconds,1)
        return self.timeMng.getTimer('delay')

    def getTimerDelay(self):
        self.timeMng.getTimer('delay').get_delay()

    def setOffsetPosition(self, offset):
        if isinstance(offset, (tuple,list)):
            if len(offset) == 2:
                self.setPos(QtCore.QPointF(offset[0],offset[1]))
                return 1
        return 0

    def updateText(self, force=False):
        if (not self.__inactive and self.timeMng.isTimerDelayPassed('delay',1) and self.__timer_delay) or force:
            self.setHtml(self.getFullText(1))

    def getFullText(self, fill_vars=False):
        if self.__textLine_Update:
            temp = ""
            temp += self.__header
            lines=self.__lines.keys()
            for i in range(min(lines),max(lines)+1):
                l=self.getLine(i)
                if l:
                    temp+=l.getFormattedText()+"<br>"
                else:
                    temp+="<br>"
            temp+=self.__footer
            self.__static_text = temp
            self.__textLine_Update=False


        if self.__var_update:
            temp=self.__static_text
            if fill_vars:
                total_vars=re.findall('[[][a-zA-Z][a-zA-Z0-9]*[]]',temp)
                for i in total_vars:
                    if i in self.__vars.keys():
                        temp=temp.replace(i,self.__vars[i])
            self.__var_update=False
            self.__var_text=temp
            return temp

        if fill_vars:
            return self.__var_text
        return self.__static_text

    def getVar(self, var_tag):
        if "["+var_tag+"]" in self.__vars.keys():
            return self.__vars["["+var_tag+"]"]
        return None

    def setVar(self, var_tag="", value=None):
        temp=re.findall('[a-zA-Z][a-zA-Z0-9]*',var_tag)[0]
        if temp == var_tag:
            self.__vars["["+var_tag+"]"]=value
            self.__var_update=True
            return self.__vars["["+var_tag+"]"]
        return None

    def getLine(self, line_number=None):
        if isinstance(line_number, int):
            if line_number in self.__lines.keys():
                return self.__lines[line_number]
        return None

    def setLine(self, line_number, text_or_textLine, face=None, color=None, size=None, align=None, bold=None, italic=None, underline=None, strikethrough=None):
        if isinstance(line_number, int):
            if isinstance(text_or_textLine, textLine):
                self.__lines[line_number] = text_or_textLine
            elif line_number in self.__lines.keys():
                self.__lines[line_number].setText(text_or_textLine)
            else:
                self.__lines[line_number]=textLine(text_or_textLine, size, color, face, bold, italic, underline, strikethrough, align, self)

            self.__inactive = False
            self.updateText(1)
            return self.__lines[line_number]


        return None

    def removeLine(self, line_number=None):
        if isinstance(line_number, int):
            if line_number in self.__lines.keys():
                return self.__lines.pop(line_number)
        return None

    def swapLines(self, line_number1, line_number2):
        if isinstance(line_number1, int) and isinstance(line_number2, int):
            if line_number1 in self.__lines.keys() and line_number2 in self.__lines.keys():
                self.__lines[line_number1], self.__lines[line_number2]= self.__lines[line_number2], self.__lines[line_number1]
                return (self.__lines[line_number1], self.__lines[line_number2])
        return None

    def getHeader(self):
        return self.__header

    def getFooter(self):
        return self.__footer

    def getDefaultFace(self):
        return self.__default_face

    def getDefaultColor(self):
        return self.__default_color

    def getDefaultSize(self):
        return self.__default_size

    def getDefaultAlignment(self):
        return self.__default_alignment

    def getDefaultBold(self):
        return self.__default_bold

    def getDefaultItalic(self):
        return self.__default_italic

    def getDefaultUnderline(self):
        return self.__default_underline

    def getDefaultStrikethrough(self):
        return self.__default_strikethrough

    def setDefaultFace(self, face=None):
        if isinstance(face, str):
            self.__default_face=face
            self.__updateHeaders()
        return self.__default_face

    def setDefaultColor(self, color=None):
        if isinstance(color, str):
            self.__default_color=color
            self.__updateHeaders()
        return self.__default_color

    def setDefaultSize(self, size=None):
        if isinstance(size, (int, float)):
            self.__default_size=size
            self.__updateHeaders()
        return self.__default_size

    def setDefaultAlignment(self, alignment=None):
        if alignment in [ALIGN_RIGHT, ALIGN_LEFT, ALIGN_CENTER]:
            self.__default_alignment=alignment
            self.__updateHeaders()
        return self.__default_alignment

    def setDefaultBold(self, is_bold=False):
        if is_bold:
            self.__default_bold=True
            self.__updateHeaders()
        return self.__default_bold

    def setDefaultItalic(self, is_italic=False):
        if is_italic:
            self.__default_italic=True
            self.__updateHeaders()
        return self.__default_italic

    def setDefaultUnderline(self, is_underline=False):
        if is_underline:
            self.__default_underline=True
            self.__updateHeaders()
        return self.__default_underline

    def setDefaultStrikethrough(self, is_strikethrough=False):
        if is_strikethrough:
            self.__default_strikethrough=True
            self.__updateHeaders()
        return self.__default_strikethrough

    def __updateHeaders(self):
        temp = textLine("!*$*!", self.__default_size, self.__default_color, self.__default_face, self.__default_bold, self.__default_italic, self.__default_underline, self.__default_strikethrough, self.__default_alignment)
        temp=temp.getFormattedText().split("!*$*!")
        self.__header = temp[0]
        self.__footer= temp[1]




class textLine():
    def __init__(self, text=None, size=None, color=None, face=None, bold=False, italic=False, underline=False, strikethrough=False, alignment=None, parent=None):

        self.parent=parent
        self.__updated = False

        self.__face = None
        self.__color = None
        self.__size = None
        self.__alignment = None
        self.__bold = None
        self.__italic = None
        self.__underline = None
        self.__strikethrough  = None

        self.__text = None
        self.__formatted_text = None

        self.setSize(size)
        self.setColor(color)
        self.setFace(face)
        self.setBold(bold)
        self.setItalic(italic)
        self.setUnderline(underline)
        self.setStrikethrough(strikethrough)
        self.setAlignment(alignment)

        self.setText(text)

    def getFace(self):
        return self.__face

    def getColor(self):
        return self.__color

    def getSize(self):
        return self.__size

    def getAlignment(self):
        return self.__alignment

    def getBold(self):
        return self.__bold

    def getItalic(self):
        return self.__italic

    def getUnderline(self):
        return self.__underline

    def getStrikethrough(self):
        return self.__strikethrough

    def getText(self):
        return self.__text

    def getFormattedText(self):
        if self.__updated:
            div=""
            font=""
            mods=""
            footer=""
            if self.__alignment:
                div="<div align='"+self.__alignment+"'>"
                footer="</div>"

            if self.__face or self.__color or self.__size:
                font="<font"
                if self.__face:
                    font = font + " face='" + self.__face + "'"
                if self.__color:
                    font = font + " color='" + self.__color+ "'"
                if self.__size:
                    font = font + " size='" + self.__size + "'"

                font=font+">"
                footer="</font>"+footer

            if self.__bold:
                mods=mods+"<b>"
                footer="</b>"+footer
            if self.__italic:
                mods=mods+"<i>"
                footer="</i>"+footer
            if self.__underline:
                mods=mods+"<u>"
                footer="</u>"+footer
            if self.__strikethrough:
                mods=mods+"<s>"
                footer="</s>"+footer

            self.__formatted_text= div + font + mods + self.__text + footer
            self.__updated = False
        return self.__formatted_text

    def setFace(self, face=None):
        if isinstance(face, str):
            self.__updated=True
            self.parent.__textLine_Update = True
            self.__face=face
        return self.__face

    def setColor(self, color=None):
        if isinstance(color, str):
            self.__updated=True
            self.parent.__textLine_Update = True
            self.__color=color
        return self.__color

    def setSize(self, size=None):
        if isinstance(size, (int, float)):
            self.__updated=True
            self.parent.__textLine_Update = True
            self.__size=str(size)
        return self.__size

    def setAlignment(self, alignment=None):
        if alignment in [ALIGN_RIGHT, ALIGN_LEFT, ALIGN_CENTER]:
            self.__updated=True
            self.parent.__textLine_Update = True
            self.__alignment=alignment
        return self.__alignment

    def setBold(self, is_bold=False):
        if is_bold:
            self.__updated=True
            self.parent.__textLine_Update = True
            self.__bold=True
        return self.__bold

    def setItalic(self, is_italic=False):
        if is_italic:
            self.__updated=True
            self.parent.__textLine_Update = True
            self.__italic=True
        return self.__italic

    def setUnderline(self, is_underline=False):
        if is_underline:
            self.__updated=True
            self.parent.__textLine_Update = True
            self.__underline=True
        return self.__underline

    def setStrikethrough(self, is_strikethrough=False):
        if is_strikethrough:
            self.__updated=True
            self.parent.__textLine_Update = True
            self.__strikethrough=True
        return self.__strikethrough

    def setText(self, text=None):
        if isinstance(text,(str,int,float)):
            self.__updated=True
            self.parent.__textLine_Update = True
            self.__text=str(text)
        return self.__text

    def isUpdated(self):
        return self.__updated

def alignTextLeft(text=None):
    if text:
        return "<div align='"+ALIGN_LEFT+"'>"+str(text)+"</div>"
    return ""

def alignTextCenter(text=None):

    if text:
        return "<div align='"+ALIGN_CENTER+"'>"+str(text)+"</div>"
    return ""

def alignTextRight(text=None):
    if text:
        return "<div align='"+ALIGN_RIGHT+"'>"+str(text)+"</div>"
    return ""

def fontFormat(text=None, size=None, color=None, face=None):
    if text and (face or color or size):
        font="<font"
        if face:
            font = font + " face='" + face + "'"
        if color:
            font = font + " color='" + color+ "'"
        if size:
            font = font + " size='" + str(size) + "'"

        font=font+">"
        return font + str(text) + "</font>"
    return text or ""

def toBold(text = None):
    if text:
        return "<b>" + str(text) + "</b>"
    return text or ""
def toItalic(text = None):
    if text:
        return "<i>" + str(text) + "</i>"
    return text or ""
def toUnderline(text = None):
    if text:
        return "<u>" + str(text) + "</u>"
    return text or ""
def toStrikethrough(text = None):
    if text:
        return "<s>" + str(text) + "</s>"
    return text or ""
def toSuperscript(text = None):
    if text:
        return "<sup>" + str(text) + "</sup>"
    return text or ""
def toSubscript(text = None):
    if text:
        return "<sub>" + str(text) + "</sub>"
    return text or ""
def toMono(text = None):
    if text:
        return "<tt>" + str(text) + "</tt>"
    return text or ""

def insertImage(source=None, width=None, height=None):
    if source:
        width = " width='"+str(width)+"'" if width else ""
        height = " height='"+str(height)+"'" if height else ""
        return "<img src='"+source+"'" + width + height + ">"
    return ""

def insertVariable(var_tag=None):
    if var_tag:
        return "["+var_tag+"]"
    return ""
