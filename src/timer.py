from time import time
class timer():
    def __init__(self,delay=0):
        self.marker = [time()]
        self.last_mark = self.marker[0]
        self.last_time_length = 0
        self.active = True
        self.__delay=delay
        self.__tick_time = time()
        self.__fps = 0

    def tick(self):
        t=time()
        u=t-self.__tick_time
        self.__fps = 1/u
        self.__tick_time=t
        return u

    def get_fps(self):
        return self.__fps

    def start(self):
        if not self.active:
            self.last_mark = time()
            self.active = True
            return 0
        return 1

    def pause(self):
        if self.active:
            self.last_time_length=self.last_time_length+(time()-self.last_mark)
            self.active=0
            return 0
        return 1

    def reset(self,start=False):
        self.last_mark = time()
        self.last_time_length = 0
        self.active = start

    def isActive(self):
        return self.active

    def elapsed(self):
        if self.active:
            return self.last_time_length+(time()-self.last_mark)
        return self.last_time_length

    def get_delay(self):
        return self.__delay

    def set_delay(self, delay=None):
        if type(delay) in [int, float]:
            self.__delay = abs(delay)
            self.reset(self.isActive())
        return self.__delay

    def delay_passed(self,reset_if_true=True):
        if self.elapsed() > self.__delay:
            if reset_if_true:
                self.reset(start=self.isActive())
            return True
        return False
