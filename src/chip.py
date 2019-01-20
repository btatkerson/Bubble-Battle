#!/usr/bin/python3

import src.app

from PyQt4 import QtCore, QtGui
from src.timer import timer
from src.animationManager import animationManager, animation
from src.timerManager import timerManager
from src.textManager import textManager, textLine
import math
import pymunk as pm
import src.blueprint as bp
import time

BODY_TYPE_STATIC = pm.Body.STATIC
BODY_TYPE_DYNAMIC = pm.Body.DYNAMIC
BODY_TYPE_KINEMATIC = pm.Body.KINEMATIC

#app=QtGui.QApplication(sys.argv)
app=src.app.app

def getBlueprintCatalog():
    return bp.getCatalog() or bp.catalog()

class ChipBody(pm.Body, bp.blueprint):
    def __init__(self, mass = 0, moment = 0, body_type = BODY_TYPE_DYNAMIC, resource_ref_name=None,prefix=None):

        pm.Body.__init__(self, mass, moment, body_type)
        bp.blueprint.__init__(self,prefix or 'ch_body')
        self.set_ref_name(resource_ref_name)
        self.add_self_to_catalog()

    def getPositionDistanceFromSphericalBodyCenter(self, body, distance=10, angle=0, offset=(0,0), degree_input=False):
        '''
        Sets body at a magnitude and angle away from the center of a spherical body.
        '''
        body_center=(0,0)
        if degree_input:
            angle=math.radians(angle)

        if isinstance(body,pm.Body) or isinstance(body, ChipBody):
            body_center = pm.Vec2d(body.position)+pm.Vec2d(offset)

        else:
            body_center = pm.Vec2d(body.chipBody.position)+pm.Vec2d(offset)
            body_radius = body.radius

        
        shift_vec = pm.Vec2d((distance+body_radius)*math.cos(angle), (distance+body_radius)*math.sin(angle))


        return body_center + shift_vec
        
    def setPositionDistanceFromSphericalBodyCenter(self, body, distance=10, angle=0, body_radius=0, offset=(0,0), degree_input=False):
        '''
        Sets body at a magnitude and angle away from the center of a spherical body.
        '''
        self.position = self.getPositionDistanceFromSphericalBodyCenter(body, distance, angle, offset, degree_input)
        return self.position

    def setAngleTangentToWorldPoint(self, point, angle_shift=0, offset=(0,0), degree_input=False):
        self.angle = self.getAngleTangentToWorldPoint(point, angle_shift, offset, degree_input)

        return self.angle  

    def getAngleTangentToWorldPoint(self, point, angle_shift=0, offset=(0,0), degree_input=False):
        if degree_input:
            angle_shift=math.radians(angle_shift)

        vec_offset=pm.Vec2d(offset)
        #vec_offset.rotate(self.angle)


        #print("VEC_OFFSET",offset,vec_offset)

        dir_vect = pm.Vec2d(point)+vec_offset-pm.Vec2d(self.position)
        dir_vect = dir_vect*(-1,-1)

        return dir_vect.angle + math.pi/2 + angle_shift
   
    def setAngleTangentToBodyCenter(self, body, angle_shift=0, offset=(0,0), degree_input=False):
        if isinstance(body,ChipBody) or isinstance(body,pm.Body):
            body_center = body.position
        else:
            body_center = body.chipBody.position

        return self.setAngleTangentToWorldPoint(body_center, angle_shift, offset, degree_input)

        
    def getAngleTangentToBodyCenter(self, body, angle_shift=0, offset=(0,0), degree_input=False):
        if isinstance(body,ChipBody) or isinstance(body,pm.Body):
            body_center = body.position + pm.Vec2d(offset)
        else:
            vec_offset=pm.Vec2d(offset)
            body_center = body.chipBody.position + vec_offset + angle_shift


        return self.getAngleTangentToWorldPoint(body_center,angle_shift,offset,degree_input)
 

    def getAngleToWorldPoint(self, point, offset=(0,0), return_degrees=False):
        offset=pm.Vec2d(offset)
        offset.rotate(self.angle)
        pos_offset=self.position+offset
        point = pm.Vec2d(point)
        ang=point-pos_offset
        if return_degrees:
            return ang.angle_degrees
        return ang.angle

    def getDistanceToWorldPoint(self, point, offset=(0,0)):
        offset=pm.Vec2d(offset)
        offset.rotate(self.angle)
        pos_offset=self.position+offset
        point = pm.Vec2d(point)
        ang=point-pos_offset
        return ang.length

    def apply_absolute_force_at_local_point(self, force, point):
        '''
        Applys a force vector to the body that goes in the direction of the 
        the world instead of the being dependent on angle of the body
        '''
        force = pm.Vec2d(force)
        force.rotate(-self.angle)
        self.apply_force_at_local_point(force,point)

    def apply_absolute_impulse_at_local_point(self, impulse, point):
        '''
        Applys an impulse vector to the body that goes in the direction of the 
        the world instead of the being dependent on angle of the body
        '''
        impulse = pm.Vec2d(impulse)
        impulse.rotate(-self.angle)
        #print('ABSOLUTE IMP',impulse)
        self.apply_impulse_at_local_point(impulse,point)
        
    def setPosition(self, x_or_tuple, y=None, offset=(0,0)):
        if type(x_or_tuple) == tuple:
            self.position = pm.Vec2d(x_or_tuple)+pm.Vec2d(offset)
            return True
        else:
            self.position = pm.Vec2d(x_or_tuple, y)+pm.Vec2d(offset)
            return True
        return False

class ChipObjectSegment(QtGui.QGraphicsRectItem, pm.Segment, bp.blueprint):
    def __init__(self, body_type=BODY_TYPE_STATIC, mass=1, a_point_or_tuple=[], b_point=None, radius=0, friction=0, elasticity=0, density=0, center_of_grav=None, color=None, scene=None, resource_ref_name=None, prefix=None):
        if not b_point:
            x1,y1,x2,y2=a_point_or_tuple[0][0],a_point_or_tuple[0][1],a_point_or_tuple[1][0],a_point_or_tuple[1][1]
        else:
            x1,y1,x2,y2=a_point_or_tuple[0],a_point_or_tuple[1],b_point[0],b_point[1]

        self.__body_type=BODY_TYPE_STATIC

        self.line_angle_adjustment=math.atan2((y2-y1),(x2-x1))
        distance_between = int(((x2-x1)**2+(y2-y1)**2)**.5)

        if radius <= 1:
            radius=1
            rect=QtCore.QRectF(0,0,distance_between+radius,radius)
        else:
            #rect=QtCore.QRectF(x1,y1-radius,x1+distance_between,y1+radius)
            rect=QtCore.QRectF(0,-radius,distance_between,2*radius)
        QtGui.QGraphicsRectItem.__init__(self,rect,scene=scene)
        #self.rotate(line_angle)

        bp.blueprint.__init__(self,prefix or 'ch_obj_seg')
        self.__eventManager=bp.eventManager()
        self.eventManager=self.getEventManager
        

        inertia = pm.moment_for_segment(mass,(x1,y1),(x2,y2),radius)
        self.chipBody = ChipBody(mass,inertia,self.__body_type)
        self.bod_segs=[x1,y1]

        pm.Segment.__init__(self, self.chipBody, (x1,y1), (x2,y2),radius=radius)

        self.cog = None
        if type(center_of_grav) == tuple:
            self.cog = pm.Vec2d(center_of_grav)
        else:
            self.cog = pm.Vec2d(self.center_of_gravity)
        self.cx, self.cy = self.cog


        if density:
            self.density=density
        if friction:
            self.friction=friction
        if elasticity:
            self.elasticity=elasticity
        if color:
            self.setBrushColor(color=color)
            self.setPenColor(color=color)

        self.hide()
        
        self.set_ref_name(resource_ref_name)
        self.add_self_to_catalog()
        self.__update_object=True
        self.updateChipObject(1)
        self.ucoi=self.__updateChipObject_Internal


    def __center_of_grav(self):
        return self.cog

    def getBodyType(self):
        return self.__body_type

    def getEventManager(self):
        return self.__eventManager

    def getEvent(self, evt=None):
        return self.__eventManager.getEvent(evt)

    def setEvent(self, evt=None, value=None):
        return self.__eventManager.setEvent(evt, value)

    def toggleEvent(self, evt=None):
        return self.__eventManager.toggleEvent(evt)


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
        self.updateChipObject(1)

    def __updateChipObject_Segment(self):
        x,y=self.chipBody.position
        x,y=self.bod_segs[0],self.bod_segs[1]
        self.setPos(x,y)
        self.chipBody.center_of_gravity=(self.cx,self.cy)

        r=(self.chipBody.angle+self.line_angle_adjustment)/(2*3.14159265)*360
        trans=QtGui.QTransform()
        trans.rotate(r)
        self.setTransform(trans)
        self.__update_object=False
     

    def __updateChipObject_Internal(self):
        self.events()
        #self.__updateChipObject_InUse()

    def updateChipObject(self, force_update=False):
        self.events()
        if self.__update_object or force_update:
            self.__updateChipObject_Segment()
        #self.translate(-self.cx,-self.cy)
        #self.translate(self.cx*2,self.cy*2)

    def events(self):
        pass

class ChipObjectSegmentChainGenerator():
    '''
    Returns a list of segment objects that connect end to end

    wrap_back = True will place a segment between the first and last vertices in the list
    rounded_corners = True will place a circle Chip Object at the vertice points to help round the joint areas off.
    '''

    def __init__(self, vertices=[], wrap_back=False, rounded_corners=True, radius=0, friction=0, elasticity=0, density=0,color=None, scene=None, resource_ref_name=None, prefix=None):
        self.chain_segments=[]
        if len(vertices) > 1:
            for i in range(len(vertices)-1):
                self.chain_segments.append(ChipObjectSegment(a_point_or_tuple=vertices[i],b_point=vertices[i+1],radius=radius,friction=friction,elasticity=elasticity,density=density,color=color,scene=scene,resource_ref_name=resource_ref_name,prefix=prefix or "ch_obj_seg_chain"))
                if rounded_corners:
                    corner=ChipObjectCircle(BODY_TYPE_STATIC,1,radius,(0,0),0,density,friction,elasticity,color, False, scene,resource_ref_name,prefix or "ch_obj_seg_chain")
                    corner.chipBody.position=tuple(vertices[i+1])
                    self.chain_segments.append(corner)

        if len(vertices) > 2 and wrap_back:
            self.chain_segments.append(ChipObjectSegment(a_point_or_tuple=vertices[-1],b_point=vertices[0],radius=radius,friction=friction,elasticity=elasticity,density=density,color=color,scene=scene,resource_ref_name=resource_ref_name,prefix=prefix or "ch_obj_seg_chain"))

        if rounded_corners:
            corner=ChipObjectCircle(BODY_TYPE_STATIC,1,radius,(0,0),0,density,friction,elasticity,color,False,scene,resource_ref_name,prefix or "ch_obj_seg_chain")
            corner.chipBody.position=tuple(vertices[0])
            self.chain_segments.append(corner)

    def getSegments(self):
        return self.chain_segments
        


class ChipObjectPolygon(QtGui.QGraphicsPolygonItem,pm.Poly,bp.blueprint):
    def __init__(self,body_type=BODY_TYPE_DYNAMIC,mass=1,vertices=[],center_of_grav=None,radius=0, transform=None, offset=None, density=None,friction=None,elasticity=None,color=None, animator_enabled=True, text_manager_enabled=False, scene=None,resource_ref_name=None, prefix=None):
        self.__body_type=body_type
        self.__verts = self.__generate_coords(vertices)
        QtGui.QGraphicsPolygonItem.__init__(self, self.__generate_coords(vertices,1), scene=scene)
        self.__color=[0,0,0,255]
        self.__collison_box_visible=True
        self.__animator_visible=True
        self.__animator_enabled=animator_enabled
        self.__text_manager_enabled = text_manager_enabled

        bp.blueprint.__init__(self, prefix or 'ch_obj_poly')
        self.__eventManager=bp.eventManager()
        self.eventManager=self.getEventManager

        if offset==None:
            offset=(0,0)

        inertia = pm.moment_for_poly(mass, vertices=self.__verts, offset=offset, radius=radius)
        self.chipBody = ChipBody(mass,inertia,body_type)

        pm.Poly.__init__(self,self.chipBody, self.__verts, transform, radius)

        self.cog = None
        if type(center_of_grav) == tuple:
            self.cog = pm.Vec2d(center_of_grav)
        else:
            self.cog = pm.Vec2d(self.center_of_gravity)
        self.cx, self.cy = self.cog


        if density:
            self.density=density
        if friction:
            self.friction=friction
        if elasticity:
            self.elasticity=elasticity

        if color:
            self.__color=color
            self.setBrushColor(color=color)
            self.setPenColor(color=color)
        else:
            self.setBrushColor(color=self.__color)
            self.setPenColor(color=self.__color)

        self.set_ref_name(resource_ref_name)
        self.add_self_to_catalog()
        

        if self.__animator_enabled:
            self.animator=animationManager(self,scene)
            self.animator.hide()
            self.__updateChipObject_InUse=self.__updateChipObject_Animator
        else:
            self.__updateChipObject_InUse=self.__updateChipObject_noAnimator

        if self.__text_manager_enabled:
            self.textManager=textManager(self.boundingRect().width(),None,None, self, scene)
            self.textManager.hide()

        self.hide()
        self.updateChipObject(1)
        self.ucoi=self.__updateChipObject_Internal

    def __center_of_grav(self):
        return self.cog

    def __generate_coords(self,vertices=None,return_qPolygon=False):
        l=[]
        if return_qPolygon:
            for x,y in vertices:
                l.append(QtCore.QPointF(x,y))

            #print(QtGui.QPolygonF(l))
            return QtGui.QPolygonF(l)

        for x,y in vertices:
            l.append([x,y])
        #print(l)
        return l

    def getBodyType(self):
        return self.__body_type

    def getEventManager(self):
        return self.__eventManager

    def getEvent(self, evt=None):
        return self.__eventManager.getEvent(evt)

    def setEvent(self, evt=None, value=None):
        return self.__eventManager.setEvent(evt, value)

    def toggleEvent(self, evt=None):
        return self.__eventManager.toggleEvent(evt)

    def toggleCollisionBoxVisibility(self, visible=None, wireframe=False, wireframe_width=1):
        if len(self.__color)==3:
            self.__color.append(255) if self.__collison_box_visible else self.__color.append(0)

        if visible == None:
            self.__collison_box_visible = not self.__collison_box_visible
        elif visible in [True,False,0,1]:
            self.__collison_box_visible=visible

        if type(visible)==float:
            self.setOpacity(visible)
        else:
            self.setOpacity(1)

        if self.__collison_box_visible:
            self.__color[3]=255
            if not wireframe:
                self.setBrushColor(color=self.__color)
            else:
                self.__color[3]=0
                self.setBrushColor(color=self.__color)
                self.__color[3]=255
            self.setPenColor(color=self.__color,radius=wireframe_width)
            return True
        else:
            self.__color[3]=0
            self.setBrushColor(color=self.__color)
            self.setPenColor(color=self.__color, radius=wireframe_width)
        return False

    def toggleAnimatorVisibility(self,visible=None):
        if self.__animator_enabled:
            if visible==None:
                self.__animator_visible = not self.__animator_visible
            elif visible in [0,1,True,False]:
                self.__animator_visible = visible

            if type(visible)==float:
                self.animator.setOpacity(visible)
            else:
                self.animator.setOpacity(1)

            if self.__animator_visible:
                self.animator.show()
                return True
            self.animator.hide()
        return False


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

    def setPenColor(self,r=0,g=0,b=0,alpha=255, radius=1, color=None):
        pen=QtGui.QPen()
        pen.setWidthF(radius)
        if color:
            r,g,b = color[0],color[1],color[2]
            if len(color) > 3:
                alpha = color[3]
                pen.setColor(QtGui.QColor(r,g,b,alpha))
                self.setPen(pen)
                return 1
            pen.setColor(QtGui.QColor(r,g,b,alpha))
            self.setPen(pen)
            return 1
        pen.setColor(QtGui.QColor(r,g,b,alpha))
        self.setPen(pen)
        return 0

    def getChipBody(self):
        return self.chipBody

    def setPosition(self,x_or_tuple=None,y=None):
        if type(x_or_tuple) == tuple:
            self.chipBody.position=x_or_tuple
        else:
            self.chipBody.position=(x_or_tuple,y)
        self.updateChipObject(1)

    def __updateChipObject_noAnimator(self):
        x,y=self.chipBody.position
        self.chipBody.center_of_gravity=(self.cx,self.cy)
        
        r=self.chipBody.angle/(2*3.14159265)*360
        
        trans=QtGui.QTransform()
        trans.rotate(r)
        self.setTransform(trans)
        self.setPos(x,y)

    def __updateChipObject_Animator(self):
        self.__updateChipObject_noAnimator()
        self.animator.updateAnimation()

    def __updateChipObject_Internal(self):
        self.events()
        self.__updateChipObject_InUse()

    def updateChipObject(self, force_update=False):
        self.events()
        if self.__body_type != BODY_TYPE_STATIC or force_update:
            self.__updateChipObject_InUse()

    def events(self):
        pass



class chipObjectStarGenerator(ChipObjectPolygon):
    def __init__(self,body_type=BODY_TYPE_DYNAMIC,mass=1,star_points=5, inner_radius=5, outer_radius=None,center_of_grav=None,corner_radius=0, transform=None, offset=None, density=None,friction=None,elasticity=None,color=None, animator_enabled=True, text_manager_enabled=False, scene=None,resource_ref_name=None, prefix=None):
        self.corner_radius = corner_radius

        ChipObjectPolygon.__init__(self,body_type,mass,self.__generate_star_coords(star_points, inner_radius, outer_radius), center_of_grav, corner_radius, transform, offset, density, friction, elasticity, color, animator_enabled, text_manager_enabled, scene, resource_ref_name, prefix or 'ch_obj_star')

    def __generate_star_coords(self, star_points, inner_radius, outer_radius=None):
        tau = 2*math.pi
        if outer_radius:
            star_points*=2

        degs = tau/star_points
        d_l = [i*degs for i in range(star_points)]

        if not outer_radius:
            #print('INNER')
            #return [[math.cos(i)*(inner_radius+self.corner_radius), math.sin(i)*(inner_radius+self.corner_radius)] for i in d_l]
            return [[math.cos(i)*inner_radius, math.sin(i)*inner_radius] for i in d_l]
        else:
            #print('OUTER')
            a,b=max(inner_radius, outer_radius),min(inner_radius, outer_radius)

            crd = 2*a*math.sin(degs)

            hlf_crd_norm = (a**2-(crd/2)**2)**.5

            #print('NORM:', hlf_crd_norm, crd, a, b)

            if b > hlf_crd_norm:
                print("CONVEX!")
            else:
                print("CONCAVE!")

            

            r=[outer_radius if i%2==0 else inner_radius for i in range(star_points)]
            l=[[r[i]*math.cos(d_l[i]), r[i]*math.sin(d_l[i])] for i in range(star_points)]
            print(l)
            return l



        


class ChipObjectBox(QtGui.QGraphicsRectItem,pm.Poly,bp.blueprint):
    def __init__(self,body_type=BODY_TYPE_DYNAMIC,mass=1,width=10,height=10,center_of_grav=None, corner_radius = 0, transform=None, rotation_lock=False, rotation=(0,0), density=None,friction=None,elasticity=None,color=None, animator_enabled=True, text_manager_enabled=False,scene=None,resource_ref_name=None,prefix=None):
        self.corner_radius=corner_radius*.75
        QtGui.QGraphicsRectItem.__init__(self,0-self.corner_radius,0-self.corner_radius,width+self.corner_radius,height+self.corner_radius,scene=scene)
        #QtGui.QGraphicsRectItem.__init__(self,-width/2,-height/2,width/2,height/2,scene=scene)
        #self.graphic=QtGui.QGraphicsPixmapItem(QtGui.QPixmap('./resources/images/car_bod2.png','.png'),scene=scene)
        #self.graphic.setOffset(0,-40)

        self.__body_type = body_type
        self.__rotation_lock = rotation_lock
        self.__rotation_min, self.__rotation_max = rotation
        self.__color=[0,0,0,255]
        self.__collison_box_visible=True
        self.__animator_visible=True
        self.__animator_enabled=animator_enabled
        self.__text_manager_enabled=text_manager_enabled


        bp.blueprint.__init__(self,prefix or 'ch_obj_box')
        self.__eventManager=bp.eventManager()
        self.eventManager=self.getEventManager
        

        inertia = pm.moment_for_box(mass,(width,height))
        self.chipBody = ChipBody(mass,inertia,body_type)

        pm.Poly.__init__(self,self.chipBody, self.__generate_coords(width,height), transform=transform,radius=corner_radius)

        self.cog = None
        if type(center_of_grav) == tuple:
            self.cog = pm.Vec2d(center_of_grav)
        else:
            self.cog = pm.Vec2d(self.center_of_gravity)
        self.cx, self.cy = self.cog


        if density:
            self.density=density
        if friction:
            self.friction=friction
        if elasticity:
            self.elasticity=elasticity

        if color:
            self.__color=color
            self.setBrushColor(color=color)
            self.setPenColor(color=color)
        else:
            self.setBrushColor(color=self.__color)
            self.setPenColor(color=self.__color)

        self.set_ref_name(resource_ref_name)

        if self.__animator_enabled:
            self.animator=animationManager(self,scene)
            self.animator.hide()
            if self.__rotation_lock:
                self.__updateChipObject_InUse=self.__updateChipObject_Animator_rotationLock
            else:
                self.__updateChipObject_InUse=self.__updateChipObject_Animator_noRotationLock
        else:
            if self.__rotation_lock:
                self.__updateChipObject_InUse=self.__updateChipObject_noAnimator_rotationLock
            else:
                self.__updateChipObject_InUse=self.__updateChipObject_noAnimator_noRotationLock

        if self.__text_manager_enabled:
            self.textManager=textManager(self.boundingRect().width(),None,None, self, scene)
            self.textManager.hide()
        
        self.hide()
        self.updateChipObject(1)
        self.add_self_to_catalog()
        self.ucoi=self.__updateChipObject_Internal

    def __center_of_grav(self):
        return self.cog

    def __generate_coords(self,width,height=1):

        #return [[-width/2,-height/2],[width/2,-height/2],[width/2,height/2],[-width/2,height/2]]
        return [[0,0],[width,0],[width,height],[0,height]]

    def getBodyType(self):
        return self.__body_type

    def getEventManager(self):
        return self.__eventManager

    def getEvent(self, evt=None):
        return self.__eventManager.getEvent(evt)

    def setEvent(self, evt=None, value=None):
        return self.__eventManager.setEvent(evt, value)

    def toggleEvent(self, evt=None):
        return self.__eventManager.toggleEvent(evt)

    def toggleCollisionBoxVisibility(self, visible=None, wireframe=False, wireframe_width=1):
        if len(self.__color)==3:
            self.__color.append(255) if self.__collison_box_visible else self.__color.append(0)

        if visible == None:
            self.__collison_box_visible = not self.__collison_box_visible
        elif visible in [True,False,0,1]:
            self.__collison_box_visible=visible

        if type(visible)==float:
            self.setOpacity(visible)
        else:
            self.setOpacity(1)

        if self.__collison_box_visible:
            self.__color[3]=255
            if not wireframe:
                self.setBrushColor(color=self.__color)
            else:
                self.__color[3]=0
                self.setBrushColor(color=self.__color)
                self.__color[3]=255
            self.setPenColor(color=self.__color,radius=wireframe_width)
            return True
        else:
            self.__color[3]=0
            self.setBrushColor(color=self.__color)
            self.setPenColor(color=self.__color, radius=wireframe_width)
        return False

    def toggleAnimatorVisibility(self,visible=None):
        if self.__animator_enabled:
            if visible==None:
                self.__animator_visible = not self.__animator_visible
            elif visible in [0,1,True,False]:
                self.__animator_visible = visible

            if type(visible)==float:
                self.animator.setOpacity(visible)
            else:
                self.animator.setOpacity(1)

            if self.__animator_visible:
                self.animator.show()
                return True
            self.animator.hide()
        return False


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

    def setPenColor(self,r=0,g=0,b=0,alpha=255, radius=1, color=None):
        pen=QtGui.QPen()
        pen.setWidthF(radius)
        if color:
            r,g,b = color[0],color[1],color[2]
            if len(color) > 3:
                alpha = color[3]
                pen.setColor(QtGui.QColor(r,g,b,alpha))
                self.setPen(pen)
                return 1
            pen.setColor(QtGui.QColor(r,g,b,alpha))
            self.setPen(pen)
            return 1
        pen.setColor(QtGui.QColor(r,g,b,alpha))
        self.setPen(pen)
        return 0

    def getChipBody(self):
        return self.chipBody

    def setPosition(self,x_or_tuple=None,y=None):
        if type(x_or_tuple) == tuple:
            self.chipBody.position=x_or_tuple
        else:
            self.chipBody.position=(x_or_tuple,y)
        self.updateChipObject(1)

    def __updateChipObject_noAnimator_noRotationLock(self):
        x,y=self.chipBody.position
        self.chipBody.center_of_gravity=(self.cx,self.cy)
        
        r=self.chipBody.angle/(2*3.14159265)*360
        trans=QtGui.QTransform()
        trans.rotate(r)
        self.setTransform(trans)
        self.setPos(x,y)
     
    def __updateChipObject_noAnimator_rotationLock(self):
        x,y=self.chipBody.position
        self.chipBody.center_of_gravity=(self.cx,self.cy)

        r=self.chipBody.angle/(2*3.14159265)*360
        trans=QtGui.QTransform()
        trans.rotate(r)
        self.setTransform(trans)
        if self.chipBody.angle <= self.__rotation_min:
            self.chipBody.angle = self.__rotation_min
        elif self.chipBody.angle >= self.__rotation_max:
            self.chipBody.angle = self.__rotation_max
        self.setPos(x,y)
                

 
    def __updateChipObject_Animator_noRotationLock(self):
        self.__updateChipObject_noAnimator_noRotationLock()
        self.animator.updateAnimation()

    def __updateChipObject_Animator_rotationLock(self):
        self.__updateChipObject_noAnimator_rotationLock()
        self.animator.updateAnimation()

    def __updateChipObject_Internal(self):
        self.events()
        self.__updateChipObject_InUse()

    def updateChipObject(self, force_update=False):
        self.events()
        if self.__body_type != BODY_TYPE_STATIC or force_update:
            self.__updateChipObject_InUse()

    '''
 
    def updateChipObject(self, force_update=False):
        self.events()

        if self.__body_type != BODY_TYPE_STATIC or force_update:
            x,y=self.chipBody.position
            self.chipBody.center_of_gravity=(self.cx,self.cy)

            if not self.__rotation_lock:
                r=self.chipBody.angle/(2*3.14159265)*360
                trans=QtGui.QTransform()
                trans.rotate(r)
                self.setTransform(trans)
            else:
                if self.chipBody.angle <= self.__rotation_min:
                    self.chipBody.angle = self.__rotation_min
                elif self.chipBody.angle >= self.__rotation_max:
                    self.chipBody.angle = self.__rotation_max
                    

            self.setPos(x,y)
        self.animator.show()

        self.animator.updateAnimation()
        #self.textManager.updateText()
    
    '''

    def events(self):
        pass




class ChipObjectCircle(QtGui.QGraphicsEllipseItem,pm.Circle,bp.blueprint):
    def __init__(self,body_type=BODY_TYPE_DYNAMIC,mass=1,radius=10,offset=(0,0),inner_radius=0,density=None,friction=None,elasticity=None,color=None,animator_enabled=True,scene=None,resource_ref_name=None, prefix=None):
        QtGui.QGraphicsEllipseItem.__init__(self,-radius,-radius,radius*2,radius*2)
        self.hide()
        bp.blueprint.__init__(self, prefix or 'ch_obj_cir')
        self.__eventManager=bp.eventManager()
        self.eventManager=self.getEventManager
        self.__body_type = body_type       
        self.__color=[0,0,0,255]
        self.__collison_box_visible=True
        self.__animator_visible=True
        self.__animator_enabled=animator_enabled

        inertia = pm.moment_for_circle(mass,inner_radius,radius,offset)
        self.chipBody = ChipBody(mass,inertia,body_type)
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
        
        if self.__animator_enabled:
            self.animator=animationManager(self,scene)
            self.animator.hide()
            self.__updateChipObject_InUse=self.__updateChipObject_Animator
        else:
            self.__updateChipObject_InUse=self.__updateChipObject_noAnimator


        self.hide()
        self.updateChipObject(1)
        self.ucoi=self.__updateChipObject_Internal

    def getEventManager(self):
        return self.__eventManager

    def getEvent(self, evt=None):
        return self.__eventManager.getEvent(evt)

    def setEvent(self, evt=None, value=None):
        return self.__eventManager.setEvent(evt, value)

    def toggleEvent(self, evt=None):
        return self.__eventManager.toggleEvent(evt)

    def getBodyType(self):
        return self.__body_type

    def toggleCollisionBoxVisibility(self, visible=None, wireframe=False, wireframe_width=1):
        if len(self.__color)==3:
            self.__color.append(255) if self.__collison_box_visible else self.__color.append(0)

        if visible == None:
            self.__collison_box_visible = not self.__collison_box_visible
        elif visible in [True,False,0,1]:
            self.__collison_box_visible=visible

        if type(visible)==float:
            self.setOpacity(visible)
        else:
            self.setOpacity(1)

        if self.__collison_box_visible:
            self.__color[3]=255
            if not wireframe:
                self.setBrushColor(color=self.__color)
            else:
                self.__color[3]=0
                self.setBrushColor(color=self.__color)
                self.__color[3]=255
            self.setPenColor(color=self.__color,radius=wireframe_width)
            return True
        else:
            self.__color[3]=0
            self.setBrushColor(color=self.__color)
            self.setPenColor(color=self.__color, radius=wireframe_width)
        return False

    def toggleAnimatorVisibility(self,visible=None):
        if self.__animator_enabled:
            if visible==None:
                self.__animator_visible = not self.__animator_visible
            elif visible in [0,1,True,False]:
                self.__animator_visible = visible

            if type(visible)==float:
                self.animator.setOpacity(visible)
            else:
                self.animator.setOpacity(1)

            if self.__animator_visible:
                self.animator.show()
                return True
            self.animator.hide()
        return False


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

    def setPenColor(self,r=0,g=0,b=0,alpha=255, radius=1, color=None):
        pen=QtGui.QPen()
        pen.setWidthF(radius)
        if color:
            r,g,b = color[0],color[1],color[2]
            if len(color) > 3:
                alpha = color[3]
                pen.setColor(QtGui.QColor(r,g,b,alpha))
                self.setPen(pen)
                return 1
            pen.setColor(QtGui.QColor(r,g,b,alpha))
            self.setPen(pen)
            return 1
        pen.setColor(QtGui.QColor(r,g,b,alpha))
        self.setPen(pen)
        return 0


    def getChipBody(self):
        return self.chipBody

    def setPosition(self,x_or_tuple=None,y=None):
        if type(x_or_tuple) == tuple:
            self.chipBody.position=x_or_tuple
        else:
            self.chipBody.position=(x_or_tuple,y)
        self.updateChipObject(1)
    
    def __updateChipObject_noAnimator(self):
        x,y=self.chipBody.position
        self.setPos(x,y)

        r=self.chipBody.angle/(2*3.14159265)*360
        self.translate(-self.radius,-self.radius)
        self.setRotation(r)
        self.translate(self.radius,self.radius)


    def __updateChipObject_Animator(self):
        self.__updateChipObject_noAnimator()
        self.animator.updateAnimation()

    def __updateChipObject_Internal(self):
        self.events()
        self.__updateChipObject_InUse()


    def updateChipObject(self, force_update=False):
        self.events()
        if self.__body_type != BODY_TYPE_STATIC or force_update:
            self.__updateChipObject_InUse()

    def events(self):
        pass


class ChipSpace(QtGui.QGraphicsScene,pm.Space,bp.blueprint):
    def __init__(self, gravity=(0,500), fps=30, parent=None, threaded=False, background_color=None, resource_ref_name=None,qApp=None, statusBar=None):
        QtGui.QGraphicsScene.__init__(self, parent=parent)
        pm.Space.__init__(self,threaded=threaded)
        bp.blueprint.__init__(self,'ch_space')

        self.__objs_all = []
        self.__objs_priority = []

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

        self.__statusBar = None
        if isinstance(statusBar,QtGui.QStatusBar):
            self.__statusBar = statusBar

        self.setBackgroundColor(color=background_color)

        self.set_ref_name(resource_ref_name)
        self.add_self_to_catalog()

    def getEventManager(self):
        return self.__eventManager or bp.eventManager()

    def getEvent(self, evt=None):
        return self.__eventManager.getEvent(evt)

    def setEvent(self, evt=None, value=None):
        return self.__eventManager.setEvent(evt, value)

    def toggleEvent(self, evt=None):
        return self.__eventManager.toggleEvent(evt)

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

    def displayStatus(self, status=None, msecs=0):
        if not self.__statusBar:
            return 0 

        if isinstance(status, (str,int,float)):
                self.__statusBar.showMessage(str(status),msecs)

    def hideStatusBar(self):
        if self.__statusBar:
            self.__statusBar.hide()

    def showStatusBar(self):
        if self.__statusBar:
            self.__statusBar.show()
        
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
        chip_object.show()
        try:
            self.addItem(chip_object.animator)
            chip_object.animator.show()
        except:
            pass

        try:
            self.addItem(chip_object.textManager)
            chip_object.textManager.show()
        except:
            pass

        chip_object.updateChipObject(1)

        self.__objs_all.append(chip_object)
        if not isinstance(chip_object,ChipObjectSegment) and not chip_object.getBodyType()==BODY_TYPE_STATIC:
            self.__objs_priority.append(chip_object)

            

    def removeChipObject(self,chip_object):
        self.remove(chip_object,chip_object.chipBody)
        self.removeItem(chip_object)
        try:
            self.__objs_priority.pop(self.__objs_priority.index(chip_object))
        except ValueError:
            pass
        return self.__objs_all.pop(self.__objs_all.index(chip_object))


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

    '''
    def getEvent(self,evt=None):
        if evt in self.getEventManager().getEventDictionary().keys():
            return self.getEventManager().getEvent(evt)
        return None
        
    def setEvent(self,evt=None,value=0):
        self.getEventManager().setEvent(evt,value)
        return self.getEventManager().getEvent(evt)
    '''

    def getEventDictionary(self,return_copy=True):
        if return_copy:
            return self.getEventManager().getEventDictionary(return_copy)
        return self.getEventManager()
        
    def isRunning(self):
        return self.__running

    def setRunning(self, running=None):
        if running in [0,False]:
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
        return 1

    def toggleRunning(self):
        self.__running = not self.__running
        if self.__running:
            self.resume()
            return 1
        else:
            self.pause()
            return 0 

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

        #print('Run stopped!')
        return 0

    def __internal_run(self):
        self.tick()
        self.step(self.getHZ())
        #self.step(1/self.getFPSActual())
        for i in self.__objs_priority:
            i.ucoi()
        self.__app.processEvents()
        time.sleep(self.getHZ())

    def events(self):
        '''
        print('Running')
        k=bp.getCatalog().find_resources_by_prefix('ch_obj',True)
        for i in k:
            j=bp.getCatalog().find_resource(i)
            j.updateChipObject()
        '''
        pass

    def mouseReleaseEvent(self,evt=None):
        pass

    def keyPressEvent(self,evt=None):
        if evt.key() == QtCore.Qt.Key_Escape:
            self.setEvent('ESC',0)
            print("Escape pressed!")

            
class gameSpace(pm.Space):
    def __init__(self, threaded=False, statusBar=None, parent=None):
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

