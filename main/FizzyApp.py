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

    def mouseMoveEvent(self):
        '''
        self.scene.events()
        self.scene.__internal_run()
        '''
        pass

class FizzyScene(ch.ChipSpace,ch.bp.blueprint):
    def __init__(self, parent=None, threaded=False, color=[0,255,255], res_name='main_game'):

        ch.ChipSpace.__init__(self, (0,200), 50, parent, threaded, color, res_name)
        #ch.ChipSpace.__init__(self, (0,0), 50, parent, threaded, color, res_name)
        ch.bp.blueprint.__init__(self,'fizz_scene')
        self.set_ref_name(res_name)
        self.add_self_to_catalog()
        evts = {'MOVE_RIGHT':0,
                'MOVE_LEFT' :0,
                'IS_IDLE':1,
                'GRAVITY': 0,
                'TEST':0}


        self.getEventManager().setEventDictionary(evts,True,True)

        '''
        Custom Initialization
        '''


        self.v_bod = ch.ChipObjectBox(ch.BODY_TYPE_DYNAMIC,180,150,40,color=[144,0,196,0],center_of_grav=(75,27.22),rotation_lock=False,scene=self,resource_ref_name='v_bod')
        self.v_bod.setPosition(240,-135)
        self.v_bod.elasticity=.05
        self.v_bod.friction=2
        self.v_bod.animator.addAnimation('car_bod',ch.animation('./resources/images/car_bod2.png','.png'),(0,-40))
        #self.v_bod.chipBody.center_of_gravity=(75,20)
        self.v_bod.animator.setCurrentAnimation('car_bod')
        self.addChipObject(self.v_bod)

        self.v_bod_top = ch.ChipObjectPolygon(ch.BODY_TYPE_DYNAMIC,135,[(0,0),(150,0),(110,-40),(40,-40)],None,0,None,(0,-40),color=[144,0,196,0],scene=self,resource_ref_name='v_bod_top')
        self.v_bod_top.setPosition(240,-125)
        self.v_bod_top.elasticity=.05
        self.v_bod_top.friction=2
        self.addChipObject(self.v_bod_top)

        ps = [ch.pm.PivotJoint(self.v_bod.chipBody,self.v_bod_top.chipBody,(0,0),(0,0)),
              ch.pm.GearJoint(self.v_bod.chipBody,self.v_bod_top.chipBody,0,1),
              ch.pm.PivotJoint(self.v_bod.chipBody,self.v_bod_top.chipBody,(75,0),(75,0)),
              ch.pm.PivotJoint(self.v_bod.chipBody,self.v_bod_top.chipBody,(150,0),(150,0))]
              
        for i in ps:
            self.add(i)



        #self.ball=ch.chipObjectStarGenerator(ch.BODY_TYPE_DYNAMIC, 20, 20, 20, corner_radius=2, elasticity=0, color=[255,255,0], resource_ref_name='star')
        self.ball = ch.ChipObjectCircle(ch.BODY_TYPE_DYNAMIC,100,30,color=[255,255,0],scene=self,resource_ref_name='ball')
        self.ball.getChipBody().position = (200,-65)
        self.ball.elasticity=.2
        self.ball.friction=10
        self.ball.setStartAngle(0)
        self.ball.setSpanAngle(270*16)
        self.addChipObject(self.ball)

        self.ball2 = ch.ChipObjectCircle(ch.BODY_TYPE_DYNAMIC,100,30,color=[255,255,0],scene=self,resource_ref_name='ball')
        self.ball2.getChipBody().position = (430,-65)
        self.ball2.elasticity=.2
        self.ball2.friction=10
        self.ball2.setStartAngle(0)
        self.ball2.setSpanAngle(270*16)
        self.addChipObject(self.ball2)

        ps = [ch.pm.PinJoint(self.v_bod.chipBody,self.ball.chipBody,(0,0),(0,0)),
              ch.pm.PinJoint(self.v_bod.chipBody,self.ball.chipBody,(0,40),(0,0)),
              ch.pm.PinJoint(self.v_bod.chipBody,self.ball2.chipBody,(150,0),(0,0)),
              ch.pm.PinJoint(self.v_bod.chipBody,self.ball2.chipBody,(150,40),(0,0)),
              #ch.pm.DampedSpring(self.ball.chipBody,self.ball2.chipBody,(0,0),(0,0),230,100,50)]
              ch.pm.PinJoint(self.ball.chipBody,self.ball2.chipBody,(0,0),(0,0))]
              
        for i in ps:
            self.add(i)

        self.little_ball = ch.ChipObjectCircle(ch.BODY_TYPE_DYNAMIC,50,40,color=[0,196,0],scene=self,resource_ref_name='little_ball')
        self.little_ball.getChipBody().position =(400,-500)
        self.little_ball.elasticity=.99
        self.addChipObject(self.little_ball)

        self.ground = ch.ChipObjectBox(ch.BODY_TYPE_STATIC,1,600,30,color=[144,0,196],scene=self,resource_ref_name='ground')
        self.ground.setPosition(0,-15)
        self.ground.elasticity=.1
        self.ground.friction=2
        self.addChipObject(self.ground)

        self.ramp = ch.ChipObjectBox(ch.BODY_TYPE_STATIC,1,100, 30, (0,15), color=[144,0,196],scene=self, resource_ref_name='ramp')

        self.ramp.setPosition(600,-15)
        self.ramp.getChipBody().angle = -3.141592654/6
        self.ramp.elasticity=.1
        self.ramp.friction=2
        self.addChipObject(self.ramp)

        self.ramp2 = ch.ChipObjectBox(ch.BODY_TYPE_STATIC,1,100, 30, (0,15), color=[144,0,196],scene=self, resource_ref_name='ramp2')

        self.ramp2.setPosition(680,-65)
        self.ramp2.getChipBody().angle = -3.141592654/3
        self.ramp2.elasticity=.1
        self.ramp2.friction=2
        self.addChipObject(self.ramp2)
        
        self.ramp3 = ch.ChipObjectBox(ch.BODY_TYPE_STATIC,1,300, 30, (0,15), color=[144,0,196],scene=self, resource_ref_name='ramp3')

        self.ramp3.setPosition(720,-115)
        self.ramp3.getChipBody().angle = -3.141592654/2
        self.ramp3.elasticity=.1
        self.ramp3.friction=2
        #self.addChipObject(self.ramp3)

        self.ramp4 = ch.ChipObjectBox(ch.BODY_TYPE_STATIC,1,200, 30, (0,15), color=[144,0,196],scene=self, resource_ref_name='ramp4')

        self.ramp4.setPosition(725,-400)
        self.ramp4.getChipBody().angle = -3*3.141592654/4
        self.ramp4.elasticity=.1
        self.ramp4.friction=2
        #self.addChipObject(self.ramp4)

        '''
        self.seg=ch.ChipObjectSegment(ch.BODY_TYPE_STATIC,1,(400,-400),(800,-200),8,0,0,0,None,[255,255,0],self,'seg1')
        self.seg=ch.ChipObjectSegment(ch.BODY_TYPE_STATIC,1,(500,-200),(1000,-200),8,2,0,0,None,[0,128,0],self,'seg1')
        self.addChipObject(self.seg)
        '''

        self.seg_chain=ch.ChipObjectSegmentChainGenerator(ch.BODY_TYPE_DYNAMIC,[[600,-200],[1000,-200],[1000,-600],[600,-600]],1,1,16,2,2,0,[0,128,0],self)
        #self.seg_chain=ch.ChipObjectSegmentChainGenerator([[700,-300],[1200,-400],[1300,-600],[900,-800],[400,-500]],0,1,8,2,2,0,[0,128,0],self)
        for i in self.seg_chain.getSegments():
            self.addChipObject(i)

        self.test_sprite=ch.ChipObjectBox(ch.BODY_TYPE_DYNAMIC,1,16*4,28*4,color=[255,0,0,255],scene=self,resource_ref_name='sprite')
        self.test_sprite.setPosition(800,-400)
        self.test_sprite.animator.addAnimation('power_up_right',ch.animation('./resources/images/cat_sprite.png','.png',6,10,[10,15],1/12),(-14*4,-12*4),4)
        self.test_sprite.animator.getAnimation('power_up_right').addSequence('test',[0,1,2,3,4,5,4,5,4,5,4,5],1)
        self.test_sprite.animator.getAnimation('power_up_right').addSequence('blast',[4,5])
        self.test_sprite.animator.addAnimation('power_up_left',ch.animation('./resources/images/cat_sprite.png','.png',6,10,[10,15],1/12),(120,-12*4),4,1)
        self.test_sprite.animator.getAnimation('power_up_left').addSequence('test',[0,1,2,3,4,5,4,5,4,5,4,5],1)
        self.test_sprite.animator.getAnimation('power_up_left').addSequence('blast',[4,5])

        self.test_sprite.animator.addAnimation('idle_right',ch.animation('./resources/images/cat_sprite.png','.png',6,10,None,1/12),(-14*4,-12*4),4)
        self.test_sprite.animator.getAnimation('idle_right').addSequence('test',[0,20,0,21],1)
        self.test_sprite.animator.addAnimation('idle_left',ch.animation('./resources/images/cat_sprite.png','.png',6,10,None,1/12),(120,-12*4),4,1)
        self.test_sprite.animator.getAnimation('idle_left').addSequence('test',[0,20,0,21],1)
        self.test_sprite.toggleCollisionBoxVisibility(0,1)
        #self.test_sprite.chipBody.angle=ch.math.pi/2
        '''
        self.test_sprite.setBrushColor(alpha=0)
        self.test_sprite.setPenColor(alpha=0)
        '''
        self.addChipObject(self.test_sprite)

        '''
        self.box_test=ch.ChipObjectBox(ch.BODY_TYPE_DYNAMIC,1,128,128,None,0,None,False,(0,0),scene=self)
        self.box_test.setPosition(728,-456)
        self.addChipObject(self.box_test)
        '''

        '''

        for i in range(5):
            o=ch.ChipObjectCircle(ch.BODY_TYPE_DYNAMIC,5,ch.random.randint(15,45),color=[ch.random.randint(128,255),ch.random.randint(128,255),ch.random.randint(128,255)],scene=self,resource_ref_name='ball')
            o.getChipBody().position=(ch.random.randint(160,760),ch.random.randint(-650,-600))
            o.density = .01
            o.elasticity = .95
            o.friction = .3
            self.addChipObject(o)
        '''



        #self.obstacle= ch.ChipObjectBox(ch.BODY_TYPE_STATIC,1,160,12,color=[0,0,255],center_of_grav=(0,6),scene=self,resource_ref_name='obstacle')
        self.obstacle= ch.ChipObjectBox(ch.BODY_TYPE_STATIC,1,160,12,color=[0,0,255],center_of_grav=(0,6),scene=self,resource_ref_name='obstacle')
        self.obstacle.getChipBody().position = 50,-350
        self.obstacle.getChipBody().angle = 3.141592654/7
        self.obstacle.friction=1

        #self.addChipObject(self.obstacle)

        #self.obstacle2= ch.ChipObjectBox(ch.BODY_TYPE_STATIC,1,160,12,color=[0,0,255],center_of_grav=(0,6),scene=self,resource_ref_name='obstacle')
        self.obstacle2= ch.ChipObjectBox(ch.BODY_TYPE_STATIC,1,160,12,color=[0,0,255],scene=self,resource_ref_name='obstacle')
        self.obstacle2.getChipBody().position = 50,-300
        self.obstacle2.friction=1

        #self.addChipObject(self.obstacle2)

        #self.obstacle3= ch.ChipObjectPolygon(ch.BODY_TYPE_KINEMATIC,3,v,color=[0,200,344],scene=self,resource_ref_name='obstacle')


        

        self.obstacle3=ch.chipObjectStarGenerator(ch.BODY_TYPE_KINEMATIC, 10, 6,40,60, elasticity=0, color=[255,153,0], resource_ref_name='star')
        self.obstacle3.getChipBody().position = 380,-450
        self.obstacle3.friction=1

        #self.obstacle3.getChipBody().angle = -3.141592654/4
        self.obstacle3.getChipBody().angle = -3.141592654/2
        self.obstacle3.getChipBody().angular_velocity=-2.5

        self.addChipObject(self.obstacle3)

        self.little_ball.setStartAngle(0)
        self.little_ball.setSpanAngle(16*325)
        self.little_ball.friction = 1

        self.setTimer('DOT', .1, 1)

        self.dots = []

        self.__dir_face=1


    '''
    def mouseDoubleClickEvent(self, evt=None):
        pass

    def mouseMoveEvent(self, evt=None):
        self.events()
        self.__internal_run()
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


    '''


    def keyPressEvent(self, evt=None):
        if evt.key() == QtCore.Qt.Key_S:
            self.setEvent('SWITCH_ROTATION_SPEED',1)
        if evt.key() == QtCore.Qt.Key_Left:
            self.setEvent('MOVE_LEFT',1)
        if evt.key() == QtCore.Qt.Key_Right:
            self.setEvent('MOVE_RIGHT',1)
        if evt.key() == QtCore.Qt.Key_Up:
            self.setEvent('JUMP',1)
        if evt.key() == QtCore.Qt.Key_Down:
            self.setEvent('DOWN',1)
        if evt.key() == QtCore.Qt.Key_G:
            self.getEventManager().toggleEvent('GRAVITY')
        if evt.key() == QtCore.Qt.Key_A:
            self.setEvent('RESET_ANGLE',1)
        if evt.key() == QtCore.Qt.Key_Escape:
            self.setEvent('EXIT',1)
            if not self.isRunning():
                self.events()

        pass

    def keyReleaseEvent(self,evt=None):
        if evt.key() == QtCore.Qt.Key_Left:
            self.setEvent('MOVE_LEFT',0)
            self.setEvent('IS_IDLE',1)
        if evt.key() == QtCore.Qt.Key_Right:
            self.setEvent('MOVE_RIGHT',0)
            self.setEvent('IS_IDLE',1)
        if evt.key() == QtCore.Qt.Key_Up:
            self.setEvent('JUMP',0)
        if evt.key() == QtCore.Qt.Key_Down:
            self.setEvent('DOWN',0)
        if evt.key() == QtCore.Qt.Key_P:
            self.setEvent('PAUSE',1)
            if not self.isRunning():
                self.resume()
                self.setEvent('PAUSE',0)
                self.run()


        pass



    def events(self):
        if self.getEvent('SWITCH_ROTATION_SPEED'):
            self.setEvent('SWITCH_ROTATION_SPEED',0)
            self.obstacle3.chipBody.angular_velocity*=-1

            
            '''

            angle_to_point=self.v_bod.chipBody.getAngleToWorldPoint(self.obstacle3.chipBody.position,offset=(90,150))
            if angle_to_point < 0:
                angle_to_point+=ch.math.pi*2

            angle_of_body = (self.v_bod.chipBody.angle+ch.math.pi/2)
            angle_of_body=angle_of_body%(ch.math.pi*2)

            #if angle_of_body < 0:
            #    angle_of_body += 2*ch.math.pi
            del_angles = angle_of_body-angle_to_point
            if del_angles < 0:
                if abs(del_angles) < ch.math.pi:
                    self.v_bod.chipBody.angular_velocity+=2
                else:
                    self.v_bod.chipBody.angular_velocity-=2
            else:
                if abs(del_angles) < ch.math.pi:
                    self.v_bod.chipBody.angular_velocity-=2
                else:
                    self.v_bod.chipBody.angular_velocity+=2
            '''


        if self.getEvent('JUMP'):
            self.v_bod.getChipBody().apply_impulse_at_local_point((4830,-4830),(10,20))
            self.v_bod.getChipBody().apply_impulse_at_local_point((-4830,-4830),(140,20))
        if self.getEvent('DOWN'):
            vec = 6000
            an = self.v_bod.chipBody.angle
            self.v_bod.getChipBody().apply_impulse_at_local_point((0,6000),(75,20))
            #self.v_bod.getChipBody().apply_absolute_impulse_at_local_point((0,6000),(75,20))
        if self.getEvent('MOVE_LEFT'):
            self.__dir_face=0
            self.setEvent('IS_IDLE',0)
            self.ball.getChipBody().angular_velocity+=-2
            self.ball2.getChipBody().angular_velocity+=-2
            #self.test_sprite.animator.setCurrentAnimation('power_up_left','blast')
            self.test_sprite.animator.setCurrentAnimation('power_up_left','default','blast')
            #self.test_sprite.animator.getCurrentAnimation().setSequenceOnCycleComplete('blast')
        if self.getEvent('MOVE_RIGHT'):
            self.__dir_face=1
            self.setEvent('IS_IDLE',0)
            self.ball.getChipBody().angular_velocity+=2
            self.ball2.getChipBody().angular_velocity+=2
            self.test_sprite.animator.setCurrentAnimation('power_up_right')
            self.test_sprite.animator.getCurrentAnimation().setSequenceOnCycleComplete('blast')
        if not self.getEvent('GRAVITY'):
            self.v_bod.getChipBody().apply_absolute_impulse_at_local_point((0,-900),(75,50))
        if self.getEvent('RESET_ANGLE'):
            self.setEvent('RESET_ANGLE')




        if self.getEvent('PAUSE'):
            print("IS running", self.isRunning())
            if self.isRunning():
                self.setEvent('PAUSE',0)
                self.pause()
        if self.getEvent('EXIT'):
            self.setRunning(False)
            print("Is running:", self.setRunning(False))
            sys.exit(0)
        if self.getEvent('IS_IDLE'):
            if self.__dir_face:
                self.test_sprite.animator.setCurrentAnimation('idle_right')
            else:
                self.test_sprite.animator.setCurrentAnimation('idle_left')

        self.ball_grav()

        print(self.eventManager().getEventDictionary())

    def ball_grav(self):
        imp = ch.pm.Vec2d(0,-700)
        imp.rotate(self.little_ball.chipBody.getAngleToWorldPoint((380,-450)))
        imp.rotate(ch.math.pi/2)
        imp=imp+ch.pm.Vec2d(0,-200)
        print(imp, self.little_ball.chipBody.getAngleToWorldPoint((380,-450)))
        self.little_ball.chipBody.apply_absolute_impulse_at_local_point(imp,(0,0))
        self.little_ball.chipBody.angle = self.little_ball.chipBody.getAngleToWorldPoint((380,-450)) - ch.math.pi/8

        if self.getTimerManager().getTimerDelayPassed('DOT'):
            dot = QtGui.QGraphicsEllipseItem(QtCore.QRectF(0,0,5,5), scene = self)
            dot.setBrush(QtGui.QColor(0,0,0))
            x,y = self.little_ball.chipBody.position
            dot.setPos(QtCore.QPointF(x-2,y-2))
            self.dots.append(dot)

        if len(self.dots) > 400:
            d=self.dots.pop(0)
            self.dots[10].setBrush(QtGui.QColor(255,255,255))
            self.dots[10].setPen(QtGui.QColor(255,255,255))
            self.dots[25].setBrush(QtGui.QColor(0,0,2000))
            self.dots[25].setPen(QtGui.QColor(0,0,200))
            self.dots[35].setBrush(QtGui.QColor(0,200,0))
            self.dots[35].setPen(QtGui.QColor(0,200,0))
            self.dots[45].setBrush(QtGui.QColor(200,200,0))
            self.dots[45].setPen(QtGui.QColor(200,200,0))
            self.dots[55].setBrush(QtGui.QColor(255,0,0))
            self.dots[55].setPen(QtGui.QColor(255,0,0))
            self.removeItem(d)
            
            

        '''
        vec = -800
        an = self.v_bod.chipBody.angle
        
        self.v_bod.getChipBody().apply_impulse_at_local_point((vec*ch.math.cos(ch.math.pi/2-an), vec*ch.math.sin(ch.math.pi/2-an)),(75,20))

        '''

        pass
                
