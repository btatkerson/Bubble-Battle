import src.app

from PyQt4 import QtCore, QtGui
from src.timer import timer
from src.timerManager import timerManager
import math
import random

app = src.app.app

class animationManager(QtGui.QGraphicsPixmapItem):
    def __init__(self, parent=None, scene=None):
        self.ANIMATION_TYPE_STATIC = 'static'
        self.ANIMATION_TYPE_SIMPLE = 'simple'
        self.ANIMATION_TYPE_COMPLEX = 'complex'
        
        QtGui.QGraphicsPixmapItem.__init__(self, parent=parent, scene=scene)
        self.animations={'default':None}
        self.animation_flags={'default':None}
        self.animation_flags['default']={'offset':None,
                                           'scale':None,
                                           'flip_horizontal':None,
                                           'flip_vertical':None,
                                           'angle_adjustment':None,
                                           'fixed_angle':None,
                                           'termination_frames':None,
                                           'animation_type':'static',
                                           'time_delay':None,
                                           'random':None,
                                           'antialias':None}

        self.parent=parent
        self.current_animation = ""
        self.animation_playing=False
        self.scale_w = 1
        self.scale_h = 1
        self.offset_adjustment=(0,0)
        self.angle_adjustment = 0
        self.rotation_lock = False

        self.__updated_transformations = False
        self.__updater=self.__nullPass

        self.__timerMng = timerManager()

    def getCurrentAnimationCycleComplete(self):
        return self.getCurrentAnimation().isCycleComplete()

    def getCurrentAnimation(self):
        return self.getAnimation(self.current_animation)

    def getAnimation(self, animation_tag=None):
        if animation_tag in self.animations.keys():
            return self.animations[animation_tag] or animation()
        return None

    def setDefaultAnimation(self, animation_tag=None):
        '''
        Sets a default animation if it already exists in the animations library.

        Returns True if animation is found, otherwise False
        '''

        if animation_tag in self.animations.keys():
            self.animations['default']=self.animations[animation_tag]
            self.animation_flags['default']=self.animation_flags[self.current_animation][animation_tag]
            return self.animations['default']
        return None


    def addAnimation(self, animation_tag=None, animation_object=None, offset=(0,0), scale=1, flip_horizontal=False, flip_vertical=False, adjusted_angle=0, fixed_angle=False, termination_frames=[], animation_type=None, time_delay=None, random_frames=False, antialias=False, set_animation_to_default=False):
        '''
        Adds animation to class dictionary, also stores basic transformation in regards to animation transformations
        animation_tag = String - The tag used to reference the animation ie "idle", "walk_right"
        animation_object = Class animation - The animation class being stored
        offset = Offset of pixmap relative to collision box
        scale = int, float or tuple - The scale for the animation 1 = 100%. If int/float given, width and height
                will be scaled equally. If (int, int) or (float, float) is given, the scaling will be calculated
                as (width, height).
        flip_horizontal = Boolean - Flips the QGraphicsPixmapItem horizontally
        flip_vertical = Boolean - Flips the QGraphicsPixmapItem vertically
        adjusted_angle = Float (Radians) - Performs a rotational transformation on the QGraphicsPixmapItem
        fixed_angle = Boolean - Locks the rotation of the QGraphicsPixmapItem
        termination_frames = List - Int Frame numbers that are acceptable to cease current animation and go to the next one. 0 = First Frame, -1 = Last frame
        animation_type = ANIMATION_TYPE - Static - Single frame, no animation, uses least resources
                                          Simple - Loops through frames but won't track the frame number, new sequence-on-completion, completion factors, etc.
                                          Complex - Uses the most resources
        time_delay = int, float - Sets frame rate in seconds. 1 = 1 second, 1/24 = 1/24 seconds. 
        random_frames = Boolean - Set to make animation play random frames of the animation (A twinkling star, for instance)
        antialias = Boolean - Toggle the antialias on animation graphics
        set_animation_to_default = Boolean - set if the new animation being added should be the new default in the manager
        '''
        if animation_tag and animation_object:
            if isinstance(animation_object,animation):
                self.animation_flags[animation_tag]={'offset':offset,
                                                    'scale':scale,
                                                    'flip_horizontal':flip_horizontal,
                                                    'flip_vertical':flip_vertical,
                                                    'angle_adjustment':adjusted_angle,
                                                    'fixed_angle':fixed_angle,
                                                    'termination_frames':termination_frames,
                                                    'animation_type':animation_type,
                                                    'time_delay':time_delay,
                                                    'random':random_frames,
                                                    'antialias':antialias}

                self.animations[animation_tag]=animation_object

                if self.animations['default']==None or set_animation_to_default:
                    self.animations['default']=animation_object
                    self.animation_flags['default']=self.animation_flags[animation_tag]
                    self.setCurrentAnimation('default')

                return animation_object
        return None

    def removeAnimation(self,animation_tag=None):
        if animation_tag in self.animations.keys():
            return self.animations.pop(animation_tag)
        return None

    def setCurrentAnimation(self, animation_tag=None, sequence=None, sequence_after_cycle_complete = None, override_termination_frame=False):
        if self.current_animation != '' and not override_termination_frame:
            if self.animation_flags[self.current_animation]['termination_frames'] != []:
                found=0
                for i in self.animation_flags[self.current_animation]['termination_frames']:
                    if self.getCurrentAnimation().isOnFrameNumber(i):
                        found = 1
                        break
                if not found:
                    return False

        if animation_tag in self.current_animation:
            return True
        if animation_tag in self.animations.keys():
            if type(self.animation_flags[animation_tag]['scale']) in [tuple,list]:
                self.scale_w=self.animation_flags[animation_tag]['scale'][0]
                self.scale_h=self.animation_flags[animation_tag]['scale'][1]
            else:
                self.scale_w=self.animation_flags[animation_tag]['scale']
                self.scale_h=self.scale_w
            if self.animation_flags[animation_tag]['flip_horizontal']:
                self.scale_w*=-1
            if self.animation_flags[animation_tag]['flip_vertical']:
                self.scale_h*=-1

            if self.animation_flags[animation_tag]['fixed_angle']:
                self.rotation_lock=True
            else:
                self.rotation_lock=False

            if self.animation_flags[animation_tag]['angle_adjustment']:
                self.angle_adjustment=self.animation_flags[animation_tag]['angle_adjustment']
            else:
                self.angle_adjustment=0

            if self.animation_flags[animation_tag]['offset']:
                self.offset_adjustment=self.animation_flags[animation_tag]['offset']
            else:
                self.offset_adjustment=(0,0)

            if self.animation_flags[animation_tag]['time_delay']:
                self.__timerMng.setTimer(animation_tag, self.animation_flags[animation_tag]['time_delay'],1)


            self.angle_adjustment=self.animation_flags[animation_tag]['angle_adjustment']
            self.setAntialias(self.animation_flags[animation_tag]['antialias'])
            self.__updated_transformations=True
            
            self.current_animation=animation_tag 

            #t=animation()
            #t.setSequenceOnCycleComplete

            self.animations[self.current_animation].setCurrentSequence(sequence)
            self.animations[self.current_animation].setSequenceOnCycleComplete(sequence_after_cycle_complete)
            #self.animations[self.current_animation].resetTimer('frame_rate',1)
            self.__timerMng.resetTimer('frame_rate',1)

            if self.animation_flags[self.current_animation]['animation_type'] == self.ANIMATION_TYPE_SIMPLE:
                self.__updateTransformations() # Initial animation update since it won't update again on it's own
                if self.animation_flags[self.current_animation]['time_delay']:
                    if self.animation_flags[self.current_animation]['fixed_angle']:
                        if self.animation_flags[self.current_animation]['random']:
                            self.__updater=self.__updateSimpleWithRotationRandom_time
                        else:
                            self.__updater=self.__updateSimpleWithRotation_time
                    else:
                        if self.animation_flags[self.current_animation]['random']:
                            self.__updater=self.__updateSimpleWithRandom_time
                        else:
                            self.__updater=self.__updateSimple_time
                else:
                    if self.animation_flags[self.current_animation]['fixed_angle']:
                        if self.animation_flags[self.current_animation]['random']:
                            self.__updater=self.__updateSimpleWithRotationRandom
                        else:
                            self.__updater=self.__updateSimpleWithRotation
                    else:
                        if self.animation_flags[self.current_animation]['random']:
                            self.__updater=self.__updateSimpleWithRandom
                        else:
                            self.__updater=self.__updateSimple
            elif self.animation_flags[self.current_animation]['animation_type'] == self.ANIMATION_TYPE_COMPLEX:
                if self.animation_flags[self.current_animation]['time_delay']:
                    if self.animation_flags[self.current_animation]['fixed_angle']:
                            self.__updater=self.__updateComplexWithRotation_time
                    else:
                            self.__updater=self.__updateComplex_time
                else:
                    if self.animation_flags[self.current_animation]['fixed_angle']:
                            self.__updater=self.__updateComplexWithRotation
                    else:
                            self.__updater=self.__updateComplex
            else:
                self.__updateComplexWithRotation()
                self.__updater=self.__nullPass




            self.updateAnimation()

        return self.animations[self.current_animation]

    def setOffsetAdjustment(self, offset=None):
        if type(offset) in [tuple,list]:
            self.offset_adjustment=(offset[0],offset[1])
            self.__updated_transformations
            return self.offset_adjustment
        return None

    def setAntialias(self, antialias=None):
        if antialias:
            self.setTransformationMode(QtCore.Qt.SmoothTransformation)
            return True
        self.setTransformationMode(QtCore.Qt.FastTransformation)
        return False
            
    def flipHorizontal(self, direction=None):
        '''
        Flips the horizontal scale, mirroring the animation horizontally.

        direction = int, float - negative numbers will flip the image in reverse
                    positive numbers will flip the image to the standard direction

                    Leaving this blank will flip the image horizontally in the opposite direction
                    it's currently in
        '''
        if direction != None:
            if direction < 0:
                self.scale_w=-abs(self.scale_w)
            else:
                self.scale_w=abs(self.scale_w)
            
        else:
            self.scale_w*=-1
        self.__updated_transformations = True

        return self.scale_w

    def flipVertical(self, direction=None):
        '''
        Flips the vertical scale, mirroring the animation vertically.

        direction = int, float - negative numbers will flip the image in reverse
                    positive numbers will flip the image to the standard direction

                    Leaving this blank will flip the image vertically in the opposite direction
                    it's currently in
        '''
        
        if direction != None:
            if direction < 0:
                self.scale_h=-abs(self.scale_h)
            else:
                self.scale_h=abs(self.scale_h)
            
        else:
            self.scale_h*=-1
        self.__updated_transformations = True
        return self.scale_h

    def setScale(self, scale=None):
        '''
        Accepts tuple or int/float.
        
        An single int/float sets both width and height to the same value

        As a tuple, (1,3) would set a width scale of 1 and a height scale of 3.

        In scaling terms: 1 = 100% original size
        '''
        if type(scale) in [list, tuple]:
            self.scale_w = scale[0]
            self.scale_h = scale[1]
        else:
            self.scale_w = scale
            self.scale_h = self.scale_w
        
        self.__updated_transformations = True
        
        return (self.scale_w, self.scale_h)

    def setAngleAdjustment(self, angle=None):
        if type(angle) in [int, float]:
            self.angle_adjustment=angle
            self.__updated_transformations = True
            return angle
        return None

    def setRotationLock(self, rotation_lock=False):
        if rotation_lock:
            self.rotation_lock=True
        else:
            self.rotation_lock=False
        return self.rotation_lock

    def __nullPass(self):
        pass

    def __updateSimpleWithRotationRandom(self):
        self.setPixmap(self.getCurrentAnimation().rotateRandomFrame())

        trans=QtGui.QTransform()
        ang=self.parent.getChipBody().angle%(2*math.pi)
        trans.translate(-self.offset_adjustment[0],-self.offset_adjustment[1])
        trans.rotateRadians(-ang+self.angle_adjustment)
        trans.translate(self.offset_adjustment[0],self.offset_adjustment[1])
        trans.scale(self.scale_w, self.scale_h)
        self.setTransform(trans)
         
        return 0

    def __updateSimpleWithRotationRandom_time(self):
        if self.__timerMng.isTimerDelayPassed(self.current_animation, 1):
            return self.__updateSimpleWithRotationRandom()

    
    def __updateSimpleWithRandom(self):
        self.setPixmap(self.getCurrentAnimation().rotateRandomFrame())
        return 0

    def __updateSimpleWithRandom_time(self):
        if self.__timerMng.isTimerDelayPassed(self.current_animation, 1):
            return self.__updateSimpleWithRandom()


    def __updateSimpleWithRotation(self):
        trans=QtGui.QTransform()
        ang=self.parent.getChipBody().angle%(2*math.pi)
        trans.translate(-self.offset_adjustment[0],-self.offset_adjustment[1])
        trans.rotateRadians(-ang+self.angle_adjustment)
        trans.translate(self.offset_adjustment[0],self.offset_adjustment[1])
        trans.scale(self.scale_w, self.scale_h)
        self.setTransform(trans)

        self.setPixmap(self.getCurrentAnimation().rotateFrame())
         
        return 0

    def __updateSimpleWithRotation_time(self):
        if self.__timerMng.isTimerDelayPassed(self.current_animation, 1):
            return self.__updateSimpleWithRotation()

    def __updateSimple(self):
        self.setPixmap(self.getCurrentAnimation().rotateFrame())
        return 0

    def __updateSimple_time(self):
        if self.__timerMng.isTimerDelayPassed(self.current_animation, 1):
            return self.__updateSimple()

    def updateAnimation(self):
        return self.__updater()

    def __updateTransformations(self):
        if self.__updated_transformations:
            trans=QtGui.QTransform()
            '''
            else:
                trans.rotateRadians(self.angle_adjustment+self.parent.chipBody.angle)
            '''
            if self.angle_adjustment and not self.rotation_lock:
                trans.translate(-self.offset_adjustment[0],-self.offset_adjustment[1])
                trans.rotateRadians(self.angle_adjustment)
                trans.translate(self.offset_adjustment[0],self.offset_adjustment[1])
            trans.scale(self.scale_w, self.scale_h)
            self.setTransform(trans)
            #self.setOffset(self.offset_adjustment)
            self.setPos(self.offset_adjustment[0],self.offset_adjustment[1])

            self.__updated_transformations = False
            return True
        return False

    def updateAnimationComplex(self, frame=None, sequence=None, sequence_after_cycle_complete=None):
        if frame != None:
            self.getCurrentAnimation().setCurrentFrameNumber(frame)
            self.setPixmap(self.getCurrentAnimation().getCurrentFrame())
            return 0

        if sequence != None:
            self.getCurrentAnimation().setCurrentSequence(sequence)

        if sequence_after_cycle_complete != None:
            self.getCurrentAnimation().setSequenceOnCycleComplete(sequence_after_cycle_complete)


        self.__updater()

    def __updateComplex(self):
        self.setPixmap(self.getCurrentAnimation().getNextFrame())
        self.__updateTransformations()

    def __updateComplexWithRotation(self):
        trans=QtGui.QTransform()
        ang=self.parent.getChipBody().angle%(2*math.pi)
        trans.translate(-self.offset_adjustment[0],-self.offset_adjustment[1])
        trans.rotateRadians(-ang+self.angle_adjustment)
        trans.translate(self.offset_adjustment[0],self.offset_adjustment[1])
        trans.scale(self.scale_w, self.scale_h)
        self.setTransform(trans)
        self.__updateTransformations()
        
        self.setPixmap(self.getCurrentAnimation().getNextFrame())

    def __updateComplex_time(self):
        if self.__timerMng.isTimerDelayPassed(self.current_animation, 1):
            return self.__updateComplex()

    def __updateComplexWithRotation_time(self):
        if self.__timerMng.isTimerDelayPassed(self.current_animation, 1):
            return self.__updateComplexWithRotation()



class animation():
    def __init__(self, source=None, file_format=None, rows=1,cols=1, frame_range=None):
        '''
        source = str - image/sprite sheet file
        file_format = str - type of image file. ex ('png')
        rows, cols = divides the sprite sheet into given rows and columns (assuming equal size grids)
        frame_range = [start frame, end frame] - if rows and columns are given, this only collects the grid frames from left to right. Ex. 3 rows, 4 cols is 12 sprite blocks (0-11). [4,7] will return the four middle row blocks.
        time_delay = int, float - If given, a timer delay will have to pass before grabbing the next frame in the animation
                                  1 = 1 second
        '''
        
        self.orig_pm=QtGui.QPixmap(source, file_format)

        self.frames=[]
        self.sequences={'original':[],
                        'default':[]}

        self.current_sequence='default'
        self.complete_cycle=0
        
        self.sprite_width, self.sprite_height = self.orig_pm.width()/cols, self.orig_pm.height()/rows
        #print(self.orig_pm.height(),self.orig_pm.width(), self.sprite_width, self.sprite_height)


        if rows > 1 or cols > 1:
            frame_count=-1
            for i in range(0,int(self.orig_pm.height()),int(self.sprite_height)):
                for j in range(0, int(self.orig_pm.width()), int(self.sprite_width)):
                    frame_count+=1
                    if frame_range:
                        if frame_range[0] <= frame_count <= frame_range[1]:
                            self.frames.append(self.orig_pm.copy(j,i,self.sprite_width,self.sprite_height))
                    else:
                        self.frames.append(self.orig_pm.copy(j,i,self.sprite_width,self.sprite_height))
        else:
            self.frames=[self.orig_pm]

        self.sequences['original']=[i for i in range(len(self.frames))]
        self.sequences['default']=[i for i in range(len(self.frames))]

        self.current_frame = 0
        self.__sequence_on_complete = None
        self.getFrame = self.getCurrentFrame

    def getCycleComplete(self):
        return self.complete_cycle

    def isCycleComplete(self, reset_if_true=True):
        if abs(self.complete_cycle)==1:
            if reset_if_true:
                self.complete_cycle=0
            return True
        return False

    def setDefaultSequence(self, sequence_or_tag=None):
        if type(sequence_or_tag) == str:
            return self.setSequence('default',sequence_or_tag)
        elif type(sequence_or_tag) == list:
            self.sequences['default'] = [i for i in self.getSequence(sequence_or_tag)]
        return self.sequences['default']

    def getSequenceOriginal(self):
        return self.sequences['original']

    def resetSequenceDefaultToOriginal(self):
        self.sequences['default']=[i for i in self.sequences['original']]

    def getAnimationWidth(self):
        return self.sprite_width

    def getAnimationHeight(self):
        return self.sprite_height

    def addSequence(self, sequence_tag=None, sequence=[], set_sequence_to_default=False):
        if sequence_tag not in self.sequences.keys():
            if type(sequence) == list:
                new_seq=[]
                frame_len=self.getTotalFrames()
                for i in sequence:
                    if i < frame_len:
                        new_seq.append(i)

                self.sequences[sequence_tag]=new_seq
                if set_sequence_to_default:
                    self.sequences['default']=new_seq
                return self.sequences[sequence_tag]
        else:
            print("Animation\"",sequence_tag,"\" already in sequence dictionary.")
            return self.sequences[sequence_tag]
        return None

    def setSequence(self, sequence_tag=None, sequence=[]):
        if sequence_tag in self.sequences.keys():
            if type(sequence) == list:
                new_seq=[]
                frame_len=self.getTotalFrames()
                for i in sequence:
                    if i < frame_len:
                        new_seq.append(i)


                self.sequences[sequence_tag]=new_seq
                return self.sequences[sequence_tag]
        print("Animation \"",sequence_tag,"\" not found in sequence dictionary.")
        return None

    def removeSequence(self, sequence_tag=None):
        if sequence_tag in self.sequences.keys():
            return self.sequences.pop(sequence_tag)

        print("Animation \"",sequence_tag,"\" not found in sequence dictionary.")
        return None

    def getSequence(self, sequence_tag=None):
        if sequence_tag in self.sequences.keys():
            return self.sequences[sequence_tag]
        print("Animation \"",sequence_tag,"\" not found in sequence dictionary.")
        return None

    def getCurrentSequence(self, return_sequence_tag=False):
        if return_sequence_tag:
            return self.current_sequence
        return self.sequences[self.current_sequence]

    def setCurrentSequence(self, sequence_tag=None):
        if sequence_tag in self.sequences.keys():
            self.current_sequence=sequence_tag
            self.current_frame=0
            self.complete_cycle=0
            return self.sequences[sequence_tag]
        self.current_sequence='default'
        return self.sequences[self.current_sequence]

    def getSequenceOnCycleComplete(self):
        return self.__sequence_on_complete

    def setSequenceOnCycleComplete(self, sequence_tag=None):
        if sequence_tag in self.sequences.keys():
            self.complete_cycle=0
            self.__sequence_on_complete = sequence_tag
            return self.__sequence_on_complete
        return None

    def setCurrentFrameNumber(self, frame_number=0):
        self.complete_cycle=0
        self.current_frame=frame_number%len(self.getCurrentSequence())
        return self.current_frame

    def getCurrentFrameNumber(self):
        return self.current_frame%len(self.getCurrentSequence())

    def isOnFirstFrame(self):
        return True if self.current_frame == 0 else False
    
    def isOnLastFrame(self):
        return True if self.current_frame == len(self.getCurrentSequence())-1 else False

    def isOnFrameNumber(self, frame_number=0):
        return True if self.current_frame == frame_number%len(self.getCurrentSequence()) else False

    def getCurrentFrame(self):
        return self.frames[self.getCurrentSequence()[self.getCurrentFrameNumber()]]

    def getTotalFrames(self):
        return len(self.frames)

    def getFrameByNumber(self, frame_number=None):
        return self.frames[frame_number]

    def rotateFrame(self):
        self.current_frame=(self.current_frame+1)%self.getTotalFrames()
        return self.frames[self.current_frame]

    def rotateRandomFrame(self):
        self.frames.append(self.frames.pop(random.randrange(0,len(self.frames))))
        return self.frames[-1]

    def getNextFrame(self):
        self.current_frame=(self.current_frame+1)%len(self.getCurrentSequence())

        if self.current_frame == 0:
            self.complete_cycle=1

            if self.getSequenceOnCycleComplete():
                self.setCurrentSequence(self.getSequenceOnCycleComplete())
                self.__sequence_on_complete=None

        return self.frames[self.getCurrentSequence()[self.current_frame]]

    def getLastFrame(self):
        if self.current_frame == 0:
            self.complete_cycle=-1
            
            if self.getSequenceOnCycleComplete():
                self.setCurrentSequence(self.getCurrentSequence())
                self.__sequence_on_complete=None

        self.current_frame=(self.current_frame-1)%len(self.getCurrentSequence())

        return self.frames[self.getCurrentSequence()[self.current_frame]]
        
