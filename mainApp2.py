from PyQt4 import QtCore, QtGui
import main.FizzyApp as fa
#import src.chip as ch
import sys

class mainWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self,parent=parent)
        self.setMinimumSize(1200,718)
        self.mainLayout = QtGui.QGridLayout(self)
        self.setLayout(self.mainLayout)

        self.gameScene = fa.FizzyScene()
        self.gameScene.setQApp(fa.app)
        self.gameView = fa.FizzyView(self.gameScene,self)
        #self.gameView.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        self.gameView.setRenderHint(QtGui.QPainter.Antialiasing)

        self.mainLayout.addWidget(self.gameView,1,1,1,1)

        self.gameScene.setRunning(True)
        self.show()
        self.gameScene.run()


    def closeEvent(self,evt=None):
        self.gameScene.pause()
        self.gameView.destroy()
        evt.accept()
        print('CLOSED!')
        sys.exit(0)




if __name__ == '__main__':
    app = fa.app

    mainApp = mainWindow()
    mainApp.show()

    sys.exit(app.exec_())

