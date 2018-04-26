from PyQt4 import QtCore, QtGui
import src.chip as ch
import sys

app = ch.app

class FizzyView(QtGui.QGraphicsView):
    def __init__(self, scene=None, parent=None):
        QtGui.QGraphicsView.__init__(self,scene,parent)

        if self.parent():
            self.setSceneRect(0,0,self.parent().width(),-self.parent().height())

        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

class FizzyScene(ch.ChipSpace,ch.bp.blueprint):
    def __init__(self, parent=None, threaded=False, color=[0,255,255], res_name='main_game'):

        ch.ChipSpace.__init__(self, (0,200), 50, parent, threaded, color, res_name)
        ch.bp.blueprint.__init__(self,'fizz_scene')
        self.set_ref_name(res_name)
        self.add_self_to_catalog()
        evts = {'MOVE_RIGHT':0,
                'MOVE_LEFT' :0,
                'TEST':0}

        self.getEventManager().setEventDictionary(evts,True,True)

        '''
        Custom Initialization
        '''

        self.ball = ch.ChipObjectCircle(ch.BODY_TYPE_DYNAMIC,1,20,color=[255,0,0],scene=self,resource_ref_name='ball')

        self.ball.getChipBody().position = (55,-450)
        self.addChipObject(self.ball)

        self.ground = ch.ChipObjectBox(ch.BODY_TYPE_STATIC,1,400,5,color=[144,0,196],scene=self,resource_ref_name='ground')
        self.ground.setPosition(200,-15)
        self.ground.elasticity=.7
        self.addChipObject(self.ground)

        for i in range(20):
            o=ch.ChipObjectCircle(ch.BODY_TYPE_DYNAMIC,5,ch.random.randint(5,30),color=[ch.random.randint(128,255),ch.random.randint(128,255),ch.random.randint(128,255)],scene=self,resource_ref_name='ball')
            o.getChipBody().position=(ch.random.randint(10,790),ch.random.randint(-550,-100))
            o.elasticity = .95
            o.density
            self.addChipObject(o)

        self.obstacle= ch.ChipObjectBox(ch.BODY_TYPE_STATIC,1,120,6,color=[0,0,255],scene=self,resource_ref_name='obstacle')
        self.obstacle.getChipBody().position = 50,-350
        self.obstacle.getChipBody().angle = 3.141592654/6
        self.obstacle.elasticity=.90

        self.addChipObject(self.obstacle)

        self.obstacle2= ch.ChipObjectBox(ch.BODY_TYPE_STATIC,1,120,6,color=[0,0,255],scene=self,resource_ref_name='obstacle')
        self.obstacle2.getChipBody().position = 50,-350
        self.obstacle2.elasticity=.90

        self.addChipObject(self.obstacle2)


    def mouseDoubleClickEvent(self, evt=None):
        pass

    def mouseMoveEvent(self, evt=None):
        pass

    def mousePressEvent(self, evt=None):
        pass
    
    def mouseReleaseEvent(self, evt=None):
        pass

    def wheelEvent(self, evt=None):
        pass




    def dragMoveEvent(self, evt=None):
        pass

    def dragEnterEvent(self, evt=None):
        pass

    def dragLeaveEvent(self, evt=None):
        pass

    def dropEvent(self, evt=None):
        pass




    def keyPressEvent(self, evt=None):
        if evt.key() == QtCore.Qt.Key_Left:
            self.setEvent('MOVE_LEFT',1)
        if evt.key() == QtCore.Qt.Key_Right:
            self.setEvent('MOVE_RIGHT',1)
        pass

    def keyReleaseEvent(self,evt=None):
        if evt.key() == QtCore.Qt.Key_Left:
            self.setEvent('MOVE_LEFT',0)
        if evt.key() == QtCore.Qt.Key_Right:
            self.setEvent('MOVE_RIGHT',0)
        pass



    def events(self):
        print(self.getEventDictionary())
        pass
                
