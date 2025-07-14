import sys
from PyQt5.QtWidgets import QApplication
from GUI.record_gui import VoiceRecorder

if __name__ == '__main__':
    app = QApplication(sys.argv)
    recorder = VoiceRecorder()
    recorder.show()
    sys.exit(app.exec_())
