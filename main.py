from PyQt6.QtWidgets import QApplication
from windows import JBackupWindow


app = QApplication([])

window = JBackupWindow()
window.show()

app.exec()
