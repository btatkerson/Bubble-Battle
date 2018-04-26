from PyQt4 import QtCore, QtGui
import src.chip as ch
import sys

class mainWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self,parent=parent)
        self.setFixedSize(824,612)
        self.mainLayout = QtGui.QGridLayout(self)
        self.setLayout(self.mainLayout)

        self.gameView = QtGui.QGraphicsView(self)
        self.gameScene = ch.ChipSpace((0,400),50,self.gameView,background_color=[0,196,196])
        self.gameScene.setQApp(app)

        self.mainLayout.addWidget(self.gameView,1,1,1,1)

        self.gameView.setScene(self.gameScene)
        self.gameView.setSceneRect(0,0,800,-600)

        self.ball = ch.ChipObjectCircle(ch.BODY_TYPE_DYNAMIC,1,20,color=[255,0,0],scene=self.gameScene,resource_ref_name='ball')


        self.ball.getChipBody().position = (400,-500)
        dx,dy=ch.pm.Vec2d(self.ball.center_of_gravity)
        print('COG-',dx,dy)
        self.ball.updateChipObject()
        

        self.ground = ch.ChipObjectBox(ch.BODY_TYPE_STATIC,1,400,30,color=[128,0,255],scene=self.gameScene,resource_ref_name='ground')
        self.ground.getChipBody().position = 200,-15


        self.obstacle= ch.ChipObjectBox(ch.BODY_TYPE_STATIC,1,60,6,color=[0,0,255],scene=self.gameScene,resource_ref_name='obstacle')
        self.obstacle.getChipBody().position = 50,-350
        self.obstacle.getChipBody().angle = 3.141592654/4
        self.obstacle2= ch.ChipObjectBox(ch.BODY_TYPE_STATIC,1,60,6,color=[0,255,0],scene=self.gameScene,resource_ref_name='obstacle')
        self.obstacle2.getChipBody().position = 50,-350




        self.gameScene.addChipObject(self.ball)
        self.gameScene.addChipObject(self.ground)
        self.gameScene.addChipObject(self.obstacle)
        self.gameScene.setRunning(True)
        self.show()
        self.gameScene.run()
        #self.gameView.scale(1,-1)


    def closeEvent(self,evt=None):
        self.gameScene.pause()
        self.gameView.destroy()
        evt.accept()
        print('CLOSED!')
        sys.exit(0)




if __name__ == '__main__':
    app = ch.app

    mainApp = mainWindow()
    mainApp.show()

    sys.exit(app.exec_())

