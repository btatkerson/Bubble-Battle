#!/usr/bin/python3
'''
      Name: blueprint.py
    Author: Benjamin A
      Date: Aug 29, 2015
    
   Purpose: This is a major component of in-game resource management. All items, creatures, objects, areas, etc.
            will have a blueprint ID unique to them that can and will be stored in the global resource catalog. 

            The blueprint class is built with the intent of being inherited by in-game resource classes and 
            allows a default prefix to be set on each object and default numeric suffixes to potentially clashing
            ID issues. 

            All objects created are able to directly copy themselves into the global catalog.

            This was originally built with the inspiration from the Neverwinter Nights' toolset. 
'''



import copy
from src.verbose import verbose

class catalog(verbose):
    def __init__(self):
        verbose.__init__(self, 1)
        self.__custom_number_index = 1
        self.__catalog = {}

    def get_catalog(self):
        return self.__catalog.copy()

    def find_resource(self, res_ref=None):
        '''
        Returns an object if it exists in the catalog. Returns None if object does not exist. 

        Any modifications done to the object will change the object in the catalog. 

        Use catalog.copy_resource() to get a UNIQUE copy of the object from the catalog
        '''
        temp_ref = clean_res_ref(res_ref)
        if temp_ref in self.__catalog.keys():
            return self.__catalog[temp_ref]
        else:
            self.verbo(("Resource \'", clean_res_ref(temp_ref), "\' not found."))
            return None

    def find_resources_by_prefix(self, prefix=None, return_key_list=False):
        temp=[]
        prefix=clean_res_ref(prefix)
        if type(prefix) == str:
            k=self.get_catalog().keys()
            for i in k:
                if i.startswith(prefix):
                    temp.append(i)
            if return_key_list:
                return temp

            d_temp = {}
            for i in temp:
                d_temp[i]=self.get_catalog()[i]
            return d_temp

        return [] if return_key_list else {}

    def copy_resource(self, res_ref=None):
        if self.find_resource(res_ref):
            return copy.copy(self.find_resource(res_ref))
        return None

    def is_resource(self, res_ref=None):
        if self.find_resource(res_ref):
            return True
        return False

    def add_resource(self,res_ref=None,resource=None, override=False):
        if self.is_resource(res_ref):
            if not override:

                self.verbo(("Resource \'",clean_res_ref(res_ref),"\' already exists"))
                return 0
            elif resource is not None:
                self.__catalog[clean_res_ref(res_ref)]=resource
                return 1

            return 0

        else:
            if resource is not None:
                self.__catalog[clean_res_ref(res_ref)]=resource
                self.verbo(("Resource \'",clean_res_ref(res_ref),"\' added to catalog."))
                return 1
            return 0

    def pop_resource(self, res_ref=None):
        if self.is_resource(res_ref):
            return self.__catalog.pop(clean_res_ref(res_ref))

    def remove_resource(self, res_ref=None):
        if self.is_resource(res_ref):
            self.__catalog.pop(clean_res_ref(res_ref))
            return 1

        self.verbo(("Resource \'", clean_res_ref(res_ref), "\' not found."))
        return 0


def clean_res_ref(res_ref=None):
    res_ref = res_ref.lower()
    acceptable_characters = [chr(i) for i in list(range(48,58))+list(range(97,123))]+['_']
    temp = ''
    for i in res_ref:
        if i == " ":
            i = "_"
        if i in acceptable_characters:
            temp+=i

    return temp

class eventManager():
    def __init__(self):
        self.__evts={}

    def getEvent(self,evt=None):
        if evt in self.__evts.keys():
            return self.__evts[evt]
        return None
        
    def setEvent(self,evt=None,value=0):
        if evt != None:
            self.__evts[evt] = value
            return self.__evts[evt] 
        return None

    def getEventDictionary(self,return_copy=True):
        '''
        getEventDictionary(bool)

        This returns a copy of the internal event dictionary or the actual
        one depending on input. 

        return_copy - By default set to True, returns a copy of the internal
                      dictionary. There is very little reason to send the
                      internal dictionary's address to any other place in the 
                      program.
        '''
        if return_copy:
            return self.__evts.copy()
        return self.__evts

    def setEventDictionary(self, evtDict=None, copy=True, override=False):
        '''
        setEventDictionary(eventManager, bool, bool)
        setEventDictionary(dict, bool, bool)

        This sets the event dictionary. 
        
         evtDict - If given an eventManager, this will copy or use the internal
                   event dictionary inside of it.

        override - Prevents overriding an event dictionary already in place

            copy - If eventManager is given, a copy of the eventManager's internal
                   event dictionary is set for this eventManager's internal dict.

                   If dict is given, a copy of the provided dict is used instead 
                   of the provided dict itself.
        '''
        if isinstance(evtDict,eventManager):
            if override or not self.__evts:
                self.__evts = evtDict.getEventDictionary(copy)
                return 1
        elif type(evtDict)==dict:
            if override or not self.__evts:
                self.__evts = evtDict.copy() if copy else evtDict
                return 1
        return 0




class blueprint():
    def __init__(self, prefix=None, custom=None, custom_catalog=None):
        if isinstance(custom_catalog,catalog):
            self.__CAT = custom_catalog
        else:
            self.__CAT = CAT 
        self.prefix = None
        self.__set_prefix(prefix)

        self.custom = None
        self.__set_custom(custom)

        self.ref_name = None

        self.__suffix = ''
        self.__suffix_gen = self.__num_suffix_str_generator()

        self.set_ref_name()

    def __num_suffix_str_generator(self):
        temp_num = 1
        while True:
            temp = list(str(temp_num))
            while len(temp) < 4:
                temp.insert(0,'0')
            temp_num += 1
            yield '_'+''.join(temp)

    def __reset_num_suffix_str_generator(self):
        self.__suffix_gen = self.__num_suffix_str_generator()

    def __get_num_suffix_str(self):
        self.__suffix = next(self.__suffix_gen)

    def __set_prefix(self,prefix=None):
        pref = clean_res_ref(prefix)
        if pref[-1] != '_':
            pref += '_'

        if len(pref) > 0 and pref != '_':
            self.prefix = pref
        else:
            self.prefix = 'bp_gen_'

    def get_prefix(self):
        return self.prefix

    def __set_custom(self,custom=None):
        if custom:
            self.custom = True
        else:
            self.custom = False

    def is_custom(self):
        return self.custom

    def set_ref_name(self, ref_name=None, ignore_catalog=False, is_copy=False):
        '''
        Ref name is the only piece of the blueprint name outside of the tag
        that will be modifiable. Ref name is preceded with a prefix denoting the object type,
        followed by the clean ref name, and ending with a suffix if and when necessary.
        'it_wep_greatsword' - an item (weapon), a greatsword 
        'it_arm_full_plate_1_0002' - an item (armor), full plate +1, 
                                     _0002 because it_arm_full_plate_1 and it_arm_full_plate_0001
                                     already exist

        IF REF_NAME CHANGES AFTER AN ITEM IS ALREADY IN THE self.__CAT.LOG, THIS WILL CHANGE THE KEY IN THE self.__CAT.LOG.

        ignore_catalog will ignore any items that are already in the catalog

        is_copy will allow a new ref name to be made without resetting the catalog key of the original item.
        It's needed, don't question it. I... just trust me.
        '''
        temp_old_name = ''
        reset_catalog_res_ref = False
        if self.ref_name and not ignore_catalog:
            temp_old_name = self.get_res_ref()
            if self.__CAT.find_resource(temp_old_name) == self:
                reset_catalog_res_ref = True
                self.__suffix = ''
                self.__reset_num_suffix_str_generator()
                
        if type(ref_name) == str:
            self.ref_name = clean_res_ref(ref_name)
            self.__CAT.verbo_Deactivate()
            while self.__CAT.is_resource(self.get_res_ref()) and not ignore_catalog:
                self.__get_num_suffix_str()
            self.__reset_num_suffix_str_generator()
        else:
            self.ref_name = 'generic'
            self.__CAT.verbo_Deactivate()
            while self.__CAT.is_resource(self.get_res_ref()):
                self.__get_num_suffix_str()
            self.__reset_num_suffix_str_generator()

        if temp_old_name != self.get_res_ref() and reset_catalog_res_ref and not is_copy:
            self.__CAT.remove_resource(temp_old_name)
            self.add_self_to_catalog()


    def get_ref_name(self):
        return self.ref_name

    def get_res_ref(self):
        if self.custom:
            cust = 'cust_'
        else:
            cust = ""

        return self.prefix + cust + self.ref_name + self.__suffix

    def add_self_to_catalog(self, override=False):
        '''
        This allows an object inheritting blueprint to ADD itself into the universal
        catalog.
        '''
        self.__CAT.verbo_Deactivate()
        self.set_ref_name(self.ref_name, override)
        if self.__CAT.is_resource(self.get_res_ref()) and self not in self.__CAT.get_catalog().values():
            if override:
                self.__CAT.verbo_Activate()
                self.__CAT.add_resource(self.get_res_ref(), self, True)
                return 1
            else:
                '''
                This will only add itself to the catalog if the address of the object is unique in the catalog.

                Both the keys and values of the universal catalog will be unique in order to keep statistics 
                separated.

                This will prevent heartache
                '''
                self.set_ref_name(self.ref_name, False)
                self.__CAT.verbo_Activate()
                self.__CAT.add_resource(self.get_res_ref(), self)
                return 1
        else:
            if self not in self.__CAT.get_catalog().values():
                self.__CAT.verbo_Activate()
                self.__CAT.add_resource(self.get_res_ref(), self)
                return 1
        self.__CAT.verbo_Activate()
        return 0

    def copy_self_to_catalog(self, override=False):
        '''
        This allows an object inheritting blueprint to COPY itself into the universal
        catalog.

        A copied object will have a unique address allowing templates to be created and
        then modified without affecting the original item.

        This could be used in-game too such in the case where you may have an ammunition item
        that has a default stack of 99 arrows. When the ammunition item is copied and arrows start getting
        depleted, the original template ammunition item object will still have 99 arrows in the stack and
        any copied instances thereafter will as well.
        '''

        self.__CAT.verbo_Deactivate()
        self.set_ref_name(self.ref_name, override, 1)
        if not self.__CAT.is_resource(self.get_res_ref()):
            if override:
                self.__CAT.verbo_Activate()
                self.__CAT.add_resource(self.get_res_ref(), copy.copy(self), True)
                return 1
            else:
                self.__CAT.verbo_Activate()
                self.__CAT.add_resource(self.get_res_ref(), copy.copy(self))
                return 0
        else:
            self.__CAT.verbo_Activate()
            self.__CAT.add_resource(self.get_res_ref(), copy.copy(self))

        self.__CAT.verbo_Activate()

CAT = catalog()

def getCatalog():
    return CAT
