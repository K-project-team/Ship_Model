from PySide2.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PySide2.QtCore import QCoreApplication
from PySide2.QtGui import QTextCursor
from configurations import *

class Terminal(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle('Terminal')
        self.setFixedHeight(300)

        self.layout=QVBoxLayout()
        self.layout.setMargin(0)
        self.setLayout(self.layout)

        self.textarea=QTextEdit()
        self.textarea.setReadOnly(True)
        self.textarea.setStyleSheet('background : '+TERMINAL_BACKGROUND_COLOR+'; color : #fff; border : none; font-family : Calibri; font-size : 12pt; padding : 10;')
        self.scrollbar=self.textarea.verticalScrollBar()
        self.layout.addWidget(self.textarea)

        self.textarea.append('WELCOME IN THE TERMINAL !\nHere you will follow the running process.')

    def _addMessage(self,color,message):
        self.textarea.setTextColor(color)
        self.textarea.append(message)
        self.textarea.moveCursor(QTextCursor.EndOfBlock)
        QCoreApplication.processEvents()


    def addErrorMessage(self,error_message):
        self._addMessage(TERMINAL_ERROR_MESSAGE_COLOR,error_message)

    def addSuccessMessage(self,success_message):
        self._addMessage(TERMINAL_SUCCESS_MESSAGE_COLOR,success_message)

    def addProcessMessage(self,process_message):
        self._addMessage(TERMINAL_PROCESS_MESSAGE_COLOR,'\n'+process_message)

    def addSubProcessMessage(self, sub_process_message):
        self._addMessage(TERMINAL_PROCESS_MESSAGE_COLOR,'\t'+sub_process_message)

    def addInformativeMessage(self,informative_message):
        self._addMessage(TERMINAL_INFORMATIVE_MESSAGE_COLOR,'\n'+informative_message)