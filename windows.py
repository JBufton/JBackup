from PyQt6.QtWidgets import QMainWindow, QPushButton

'''The main application window'''
class JBackupWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JBackup")
        
        testButton = QPushButton("Test Button")
        
        self.setCentralWidget(testButton)
        