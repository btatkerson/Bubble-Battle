import src.timer as t

class timerManager():
    def __init__(self):
        self.__timers={}
        self.getTimerDelayPassed=self.isTimerDelayPassed


    def isTimerDelayPassed(self, timer=None, reset_if_delay_passed=True):
        if timer in self.__timers.keys():
            return self.__timers[timer].delay_passed(reset_if_delay_passed)
        return None

    def getTimerTimeBetweenTicks(self, timer=None):
        if timer in self.__timers.keys():
            return 1/self.__timers[timer].get_fps()
        return None

    def setTimerDelay(self, timer=None, delay=None):
        if type(delay) not in [int, float]:
            return None

        if timer in self.__timers.keys():
            return self.__timers[timer].set_delay(delay)
        return None

    def getTimerDelay(self, timer=None):
        if timer in self.__timers.keys():
            return self.__timers[timer].get_delay()
        return None

    def tickTimer(self, timer=None):
        if timer in self.__timers.keys():
            return self.__timers[timer].tick()
        return None

    def pauseTimer(self, timer=None):
        if timer in self.__timers.keys():
            return self.__timers[timer].pause()
        return None

    def isTimerActive(self, timer=None):
        if timer in self.__timers.keys():
            return self.__timers[timer].isActive()
        return None

    def elapsedTimer(self, timer=None):
        if timer in self.__timers.keys():
            return self.__timers[timer].elapsed()
        return None
        
    def resetTimer(self, timer=None, start_on_reset=None):
        if timer in self.__timers.keys():
            return self.__timers[timer].reset(start_on_reset)
        return None
        
    def startTimer(self, timer=None):
        if timer in self.__timers.keys():
            return self.__timers[timer].start()
        return None

    def getTimer(self,timer=None):
        if timer in self.__timers.keys():
            return self.__timers[timer]
        return None

    def setTimer(self,timer=None,value=0,startTimer=False):
        if timer != None:
            if isinstance(value,t.timer):
                self.__timers[timer] = value
            elif type(value) in [float,int]:
                self.__timers[timer] = t.timer(value)
            else:
                self.__timers[timer] = t.timer(0)

            self.__timers[timer].reset(startTimer)
            return self.__timers[timer] 
        return None

    def getTimerDictionary(self,return_copy=True):
        '''
        getTimerDictionary(bool)

        This returns a copy of the internal timer dictionary or the actual
        one depending on input. 

        return_copy - By default set to True, returns a copy of the internal
                      dictionary. There is very little reason to send the
                      internal dictionary's address to any other place in the 
                      program.
        '''
        if return_copy:
            return self.__timers.copy()
        return self.__timers

    def setTimerDictionary(self, timerDict=None, copy=True, override=False):
        '''
        setTimerDictionary(timerManager, bool, bool)
        setTimerDictionary(dict, bool, bool)

        This sets the timer dictionary. 
    
       timerDict - If given an timerManager, this will copy or use the internal
                   timer dictionary inside of it.

        override - Prtimers overriding an timer dictionary already in place

            copy - If timerManager is given, a copy of the timerManager's internal
                   timer dictionary is set for this timerManager's internal dict.

                   If dict is given, a copy of the provided dict is used instead 
                   of the provided dict itself.
        '''
        if isinstance(timerDict,timerManager):
            if override or not self.__timers:
                self.__timers = timerDict.getTimerDictionary(copy)
                return 1
        elif type(timerDict,dict):
            if override or not self.__timers:
                self.__timers = timerDict.copy() if copy else timerDict
                return 1
        return 0


