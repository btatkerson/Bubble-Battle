#!/usr/bin/python3

from PyQt4 import QtCore, QtGui
from src.timer import timer
from src.timerManager import timerManager
import pymunk as pm
import src.blueprint as bp
import random
import sys
import time

BODY_TYPE_STATIC = pm.Body.STATIC
BODY_TYPE_DYNAMIC = pm.Body.DYNAMIC
BODY_TYPE_KINEMATIC = pm.Body.KINEMATIC

app=QtGui.QApplication(sys.argv)

def getBlueprintCatalog():
    return bp.getCatalog() or bp.catalog()

class ChipObjectBox(QtGui.QGraphicsRectItem,pm.Poly,bp.blueprint):
    def __init__(self,body_type=BODY_TYPE_DYNAMIC,mass=1,width=10,height=10,offset=(0,0),density=None,friction=None,elasticity=None,color=None,scene=None,resource_ref_name=None):
        #QtGui.QGraphicsEllipseItem.__init__(-radius,-radius,radius*2,radius*2)
        QtGui.QGraphicsRectItem.__init__(self,0,0,width,height,scene=scene)
        #QtGui.QGraphicsRectItem.__init__(self,-width/2,-height/2,width/2,height/2,scene=scene)
        bp.blueprint.__init__(self,'ch_obj_box')
        self.__eventManager=bp.eventManager()
        self.eventManager=self.getEventManager
        

        inertia = pm.moment_for_box(mass,(width,height))
        self.chipBody = pm.Body(mass,inertia,body_type)

        pm.Poly.__init__(self,self.chipBody, self.__generate_coords(width,height))

        self.cx, self.cy = pm.Vec2d(self.center_of_gravity)

        if density:
            self.density=density
        if friction:
            self.friction=friction
        if elasticity:
            self.elasticity=elasticity
        if color:
            self.setBrushColor(color=color)
            self.setPenColor(color=color)

        self.set_ref_name(resource_ref_name)
        self.add_self_to_catalog()
        self.show()
        self.updateChipObject()

    def __generate_coords(self,width,height=1):
        #return [[-width/2,-height/2],[width/2,-height/2],[width/2,height/2],[-width/2,height/2]]
        return [[0,0],[width,0],[width,height],[0,height]]


    def getEventManager(self):
        return self.__eventManager

    def setBrushColor(self,r=0,g=0,b=0,alpha=255,color=None):
        if color:
            r,g,b = color[0],color[1],color[2]
            if len(color) > 3:
                alpha = color[3]
                self.setBrush(QtGui.QColor(r,g,b,alpha))
                return 1
            self.setBrush(QtGui.QColor(r,g,b))
            return 1
        self.setBrush(QtGui.QColor(r,g,b,alpha))

    def setPenColor(self,r=0,g=0,b=0,alpha=255,color=None):
        if color:
            r,g,b = color[0],color[1],color[2]
            if len(color) > 3:
                alpha = color[3]
                self.setPen(QtGui.QColor(r,g,b,alpha))
                return 1
            self.setPen(QtGui.QColor(r,g,b))
            return 1
        self.setPen(QtGui.QColor(r,g,b,alpha))
        return 0

    def getChipBody(self):
        return self.chipBody

    def setPosition(self,x_or_tuple=None,y=None):
        if type(x_or_tuple) == tuple:
            self.chipBody.position=x_or_tuple
        else:
            self.chipBody.position=(x_or_tuple,y)
        self.updateChipObject()

    def updateChipObject(self):
        self.events()
        x,y=self.chipBody.position
        self.chipBody.center_of_gravity=(self.cx,self.cy)
        print('pos',self.chipBody.position)
        print('Cs',self.cx,self.cy)
        

        r=self.chipBody.angle/(2*3.14159265)*360
        
        trans=QtGui.QTransform()
        trans.rotate(r)
        self.setTransform(trans)
        self.setPos(x,y)
        #self.translate(-self.cx,-self.cy)
        #self.translate(self.cx*2,self.cy*2)

    def events(self):
        pass




class ChipObjectCircle(QtGui.QGraphicsEllipseItem,pm.Circle,bp.blueprint):
    def __init__(self,body_type=BODY_TYPE_DYNAMIC,mass=1,radius=10,offset=(0,0),inner_radius=0,density=None,friction=None,elasticity=None,color=None,scene=None,resource_ref_name=None):
        QtGui.QGraphicsEllipseItem.__init__(self,-radius,-radius,radius*2,radius*2)
        #QtGui.QGraphicsEllipseItem.__init__(self,0,0,radius*2,radius*2,scene=scene)
        bp.blueprint.__init__(self,'ch_obj_cir')
        self.__eventManager=bp.eventManager()
        self.eventManager=self.getEventManager
        

        inertia = pm.moment_for_circle(mass,inner_radius,radius,offset)
        self.chipBody = pm.Body(mass,inertia,body_type)
        pm.Circle.__init__(self, self.chipBody, radius, offset)

        if density:
            self.density=density
        if friction:
            self.friction=friction
        if elasticity:
            self.elasticity=elasticity
        if color:
            self.setBrushColor(color=color)
            self.setPenColor(color=color)

        self.set_ref_name(resource_ref_name)
        self.add_self_to_catalog()
        self.updateChipObject()

    def getEventManager(self):
        return self.__eventManager

    def setBrushColor(self,r=0,g=0,b=0,alpha=255,color=None):
        if color:
            r,g,b = color[0],color[1],color[2]
            if len(color) > 3:
                alpha = color[3]
                self.setBrush(QtGui.QColor(r,g,b,alpha))
                return 1
            self.setBrush(QtGui.QColor(r,g,b))
            return 1
        self.setBrush(QtGui.QColor(r,g,b,alpha))

    def setPenColor(self,r=0,g=0,b=0,alpha=255,color=None):
        if color:
            r,g,b = color[0],color[1],color[2]
            if len(color) > 3:
                alpha = color[3]
                self.setPen(QtGui.QColor(r,g,b,alpha))
                return 1
            self.setPen(QtGui.QColor(r,g,b))
            return 1
        self.setPen(QtGui.QColor(r,g,b,alpha))
        return 0

    def getChipBody(self):
        return self.chipBody

    def setPosition(self,x_or_tuple=None,y=None):
        if type(x_or_tuple) == tuple:
            self.chipBody.position=x_or_tuple
        else:
            self.chipBody.position=(x_or_tuple,y)
        self.updateChipObject()

    def updateChipObject(self):
        self.events()
        x,y=self.chipBody.position
        self.setPos(x,y)

        '''
        r=self.chipBody.angle/(2*3.14159265)*360
        self.translate(-self.radius,-self.radius)
        self.setRotation(r)
        self.translate(self.radius,self.radius)
        '''

    def events(self):
        pass


class ChipSpace(QtGui.QGraphicsScene,pm.Space,bp.blueprint):
    def __init__(self, gravity=(0,500), fps=30, parent=None, threaded=False, background_color=None, resource_ref_name=None,qApp=None):
        QtGui.QGraphicsScene.__init__(self, parent=parent)
        pm.Space.__init__(self,threaded=threaded)
        bp.blueprint.__init__(self,'ch_space')

        self.__objs = []

        self.__timerManager=timerManager()
        self.timerManager=self.getTimerManager

        self.__eventManager=bp.eventManager()
        self.eventManager=self.getEventManager

        self.gravity = pm.Vec2d(gravity)

        self.__app=qApp or app

        self.__bodies={}

        self.__fps=0
        self.__hz=0
        self.setFPS(fps)

        self.__running=False
        self.__timer=timer()
        self.__timer.reset(self.__running)

        self.setBackgroundColor(color=background_color)

        self.set_ref_name(resource_ref_name)
        self.add_self_to_catalog()

    def getEventManager(self):
        return self.__eventManager or bp.eventManager()

    def getTimerManager(self):
        return self.__timerManager or timerManager()

    def getTimer(self, timer=None):
        return self.__timerManager.getTimer(timer)

    def setTimer(self, timer=None, value=0, startTimer=False):
        return self.__timerManager.setTimer(timer, value, startTimer)

    def setQApp(self,QApp=None):
        if isinstance(QApp,QtGui.QApplication):
            self.__app = QApp
            return 1
        return 0

    def getQApp(self):
        return self.__app

    def setBackgroundColor(self,r=0,g=0,b=0,alpha=255,color=None):
        if color:
            r,g,b = color[0],color[1],color[2]
            if len(color) > 3:
                alpha = color[3]
                self.setBackgroundBrush(QtGui.QColor(r,g,b,alpha))
                return 1
            self.setBackgroundBrush(QtGui.QColor(r,g,b))
            return 1
        self.setBackgroundBrush(QtGui.QColor(r,g,b,alpha))
        return 0

    def addChipObject(self,chip_object):
        self.add(chip_object,chip_object.chipBody)
        self.addItem(chip_object)
        self.__objs.append(chip_object)

    def removeChipObject(self,chip_object):
        self.remove(chip_object,chip_object.chipBody)
        self.removeItem(chip_object)
        return self.__objs.pop(self.__objs.index(chip_object))

    def getGravity(self):
        return self.gravity

    def setGravity(self,y_dir_or_coord):
        if type(y_dir_or_coord) in [float,int]:
            self.gravity = y_dir_or_coord
            return self.gravity
        if type(y_dir_or_coord) in (set):
            self.gravity=pm.Vec2d(y_dir_or_coord)
            return self.gravity
        if isinstance(y_dir_or_coord,pm.Vec2d):
            self.gravity=y_dir_or_coord
            return self.gravity
        else:
            self.gravity=(500,0)

    def getEvent(self,evt=None):
        if evt in self.getEventManager().keys():
            return self.getEventManager()[evt]
        return None
        
    def setEvent(self,evt=None,value=0):
        self.getEventManager().setEvent(evt,value)
        return self.getEventManager().getEvent(evt)

    def getEventDictionary(self,return_copy=True):
        if return_copy:
            return self.getEventManager().getEventDictionary(return_copy)
        return self.getEventManager()
        
    def isRunning(self):
        return self.__running

    def setRunning(self, running=None):
        if running == [0,False]:
            self.__timer.pause()
            self.__running = False
            return 0
        else:
            self.__timer.start()
            self.__running = True
            return 1
        return self.isRunning()

    def pause(self):
        self.__timer.pause()
        self.__running=False
        return 0

    def resume(self):
        self.__timer.start()
        self.__running=True
        return run()

    def toggleRunning(self):
        self.__running = not self.__running

    def tick(self):
        self.__timer.tick()
        return 1

    def getFPSActual(self):
        '''
        Returns the actual Frames Per Second based on the internal cycle tick

        This is what the user is seeing.
        '''
        return self.__timer.get_fps()

    def getFPS(self):
        '''
        Returns the FPS set by user.
        
        This is the FPS the QGraphicsScene and pymunk.Space are SUPPOSED to run at.
        '''
        return self.__fps

    def getHZ(self):
        '''
        Returns x seconds per frame set by user.

        If FPS = 30, function returns 1/30 = 0.0333
        '''
        return self.__hz

    def setFPS(self, fps=30):
        '''
        Sets internal FPS
        '''
        if fps:
            self.__fps = int(abs(fps))
            self.__hz = 1/self.__fps
        return 1

    def run(self):
        while self.__running:
            self.events()
            self.__internal_run()

        print('Run stopped!')
        return 0

    def __internal_run(self):
        self.tick()
        self.step(self.getHZ())
        for i in self.__objs:
            i.updateChipObject()
        self.__app.processEvents()
        time.sleep(self.getHZ())

    def events(self):
        print('Running')
        k=bp.getCatalog().find_resources_by_prefix('ch_obj',True)
        for i in k:
            j=bp.getCatalog().find_resource(i)
            j.updateChipObject()
        pass

    def mouseReleaseEvent(self,evt=None):
        pass

    def keyPressEvent(self,evt=None):
        if evt.key() == QtCore.Qt.Key_Escape:
            self.setEvent('ESC',0)
            print("Escape pressed!")

            
class gameSpace(pm.Space):
    def __init__(self, threaded=False, parent=None):
        pm.Space.__init__(self,threaded=threaded)
        self.gravity = pm.Vec2d(0,900.0)
        mass = 1
        radius = 20
        inertia = pm.moment_for_circle(mass,0,radius)

        body = pm.Body(mass,inertia)
        body.position=(400,-300)
        
        shape = pm.Circle(body,radius)
        
        self.add(body,shape)

        cir = QtGui.QGraphicsEllipseItem(0,0,radius,radius,scene=parent)
        cir.setBrush(QtGui.QBrush(QtGui.QColor(0,0,0)))
        
        x,y=body.position
        cir.setPos(x,y)

        parent.addItem(cir)

