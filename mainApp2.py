from PyQt4 import QtCore, QtGui
import main.FizzyApp as fa
#import src.chip as ch
import sys

class mainWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self,parent=parent)
        self.statusBar=QtGui.QStatusBar(self)
        self.setMinimumSize(1200,718)
        self.mainLayout = QtGui.QGridLayout(self)
        self.setLayout(self.mainLayout)
        
        #self.showFullScreen()
        self.showMaximized()

        self.gameScene = fa.FizzyScene(threaded=True, statusBar=self.statusBar)
        self.gameScene.setQApp(fa.app)
        self.gameView = fa.FizzyView(self.gameScene,self)
        self.gameScene.parent=self.gameView
        
        #self.gameView.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        self.gameView.setRenderHint(QtGui.QPainter.Antialiasing)

        self.mainLayout.addWidget(self.gameView,1,1,1,1)
        self.mainLayout.addWidget(self.statusBar,2,1,1,1)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        font=QtGui.QFont('Ubuntu Mono', 12, 0)
        self.statusBar.setFont(font)

        #self.statusBar.showMessage("This is my test",5000)



        self.gameScene.setRunning(True)
        self.show()
        self.gameScene.run()

    def displayStatus(self, status=None):
        if isinstance(status, (int,float,str)):
            self.statusBar.showMessage(str(status))
            return 1
        return 0


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

