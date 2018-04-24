'''
      Name: verbose.py
    Author: Benjamin A
   Purpose: Allows verbosity control that is easily implemented/inherited into classes,
'''

class verbose():
    def __init__(self,active=False, separator=''):
        self.activated = active
        self.separator = separator
        self.say = self.verbo

    def verbo_toggle(self,active=None):
    # Toggles the global verbosity for the class by default OR sets global verbosity to input 'active'
        if active == None:
            if self.activated:
                self.activated = False
            else:
                self.activated = True
        else:
            self.activated = active

    def verbo_isActivated(self):
    # Returns verbosity activation status
        if self.activated:
            return True
        return False

    def verbo_Activate(self):
    # Activates global verbosity for class
        self.activated = True

    def verbo_Deactivate(self):
    # Deactivates global verbosity for class
        self.activated = False

    def verbo_set_separator(self, sep=None):
        if sep or sep == '':
            if type(sep) == str:
                self.separator = sep
                return 1
        self.separator = ' '
        return 0


    def verbo(self,statement=None,override=False):
    # Prints input 'statement' if input 'override' is True OR attribute 'self.activated' is True.
        if override or self.verbo_isActivated():
            if type(statement) == tuple:
                for i in statement:
                    print(i, end=self.separator)
                print('')
                return 1

            elif type(statement) == str:
                print(statement)
                return 1

            return 0
