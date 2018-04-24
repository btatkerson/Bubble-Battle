#!/usr/bin/python3

from PyQt4 import QtCore, QtGui
from timer import timer
import pymunk as pm
import blueprint as bp
import random
import sys
import time

BODY_TYPE_STATIC = pm.Body.STATIC
BODY_TYPE_DYNAMIC = pm.Body.DYNAMIC
BODY_TYPE_KINEMATIC = pm.Body.KINEMATIC

class mainWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self,parent=parent)
        self.setFixedSize(824,612)
        self.mainLayout = QtGui.QGridLayout(self)
        self.setLayout(self.mainLayout)

        self.gameView = QtGui.QGraphicsView(self)
        self.gameScene = gameWindow(self.gameView)
        self.mainLayout.addWidget(self.gameView,1,1,1,1)

        self.gameView.setScene(self.gameScene)
        self.gameView.setSceneRect(0,0,800,-600)
        #self.gameView.scale(1,-1)

class ChipObjectCircle(QtGui.QGraphicsEllipseItem,pm.Circle,bp.blueprint):
    def __init__(self,body_type=BODY_TYPE_DYNAMIC,mass=1,radius=10,offset=(0,0),inner_radius=0,density=None,friction=None,elasticity=None,color=None,scene=None,resource_ref_name=None):
        #QtGui.QGraphicsEllipseItem.__init__(-radius,-radius,radius*2,radius*2)
        QtGui.QGraphicsEllipseItem.__init__(0,0,radius*2,radius*2,scene=scene)
        bp.blueprint.__init__(self,'ch_obj_cir')

        inertia = pm.moment_for_circle(mass,inner_radius,radius,offset)
        self.chipBody = pm.Body(mass,inertia,body_type)
        pm.Circle.__init__(self, chipBody, radius, offset)
        if density:
            self.density=density
        if friction:
            self.friction=friction
        if elasticity:
            self.elasticity=elasticity
        if color:
            self.setBrush(color)
            self.setPen(color)

        self.set_ref_name(resource_ref_name)
        self.add_self_to_catalog()

    def updateChipObject(self):
        x,y=self.chipBody.position
        r=self.chipBody.angle/(2*3.14159265)*360
        self.setPos(x,y)
        self.translate(-self.radius,-self.radius)
        self.setRotation(r)
        self.translate(self.radius,self.radius)






class ChipSpace(QtGui.QGraphicsScene,pm.Space,bp.blueprint):
    def __init__(self, gravity=(500,0), fps=30, parent=None, threaded=False, resource_ref_name=None):
        QtGui.QGraphicsScene.__init__(self, parent=parent)
        pm.Space.__init__(self,threaded=threaded)
        bp.blueprint.__init__(self,'ch_space')
        self.gravity = pm.Vec2d(gravity)

        self.__evts={}
        self.__bodies={}

        self.__fps=0
        self.__hz=0
        self.setFPS(fps)

        self.__running=False
        self.__timer=timer()
        self.__timer.reset(self.__running)
        self.set_ref_name(resource_ref_name)
        self.add_self_to_catalog()

    def addChipObject(self,chip_object):
        self.add(chip_object)
        self.addItem(chip_object)

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
        if evt:
            return self.__evts[evt]
        return None
        
    def setEvent(self,evt=None,value=0):
        self.__evts[evt] = value
        return self.__evts[evt] 

    def getEventDictionary(self,return_copy=True):
        if return_copy:
            return self.__evts.copy()
        return self.__evts
        
    def isRunning(self):
        return self.__running

    def setRunning(self, running=None):
        if running != [0,None,False]:
            self.__timer.pause()
            self.__running = False
            return 0
        self.__timer.start()
        self.__running = True
        return 1

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
        return 0

    def __internal_run(self):
        self.tick()
        app.processEvents()
        time.sleep(self.getHZ())

    def events(self):
        pass

    def mouseReleaseEvent(self,evt=None):
        pass

    def keyPressEvent(self,evt=None):
        if evt.key() == QtCore.Qt.Key_Escape:
            self.setEvent('ESC',0)
            print("Escape pressed!")

    '''
    def run(self,evt=None):
        h=600
        self.running=True
        while self.running:
            #print('pos:',self.body.position)
            x,y=self.body.position
            if y > 10:
                self.body.moment =pm.moment_for_circle(1,0,20)
                self.body.velocity = (0,0)
                y=-h
                print('pos:',self.body.position)
                print('moment',self.body.moment)
                print('velocity',self.body.velocity)
                self.body.position = x,y
            self.cir.setPos(x,y)
            self.space.step(.02)
            app.processEvents()
            time.sleep(.02)
    '''
            
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

