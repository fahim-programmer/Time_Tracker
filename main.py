from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import Qt
import time
# import cv2
import sqlite3
from datetime import datetime, date

class Storage:
    def __init__(self, dbName="logging.db") -> None:
        # Connect to the database (or create it if it doesn't exist)
        self.conn = sqlite3.connect(dbName)
        self.setup()

    def setup(self):
        # Create a table for the data
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS data (
                date TEXT PRIMARY KEY,
                seconds REAL
            )
        ''')

    def record(self, year, month, day, timeConsumed):
        date_ = date(year, month, day)
        strTime = date_.strftime(r"%Y-%m-%d")
        self.conn.execute(f'INSERT OR REPLACE INTO data (date, seconds) VALUES (?,?)', (strTime, timeConsumed,))
        self.conn.commit()

    def get(self):
        # Query the database and print the results
        cursor = self.conn.execute('SELECT * FROM data')
        for row in cursor:
            print(datetime.strptime(row[0], "%Y-%m-%d"), row[1])

    def getSpecific(self, year, month, day):
        date_ = date(year, month, day)
        strTime = date_.strftime(r"%Y-%m-%d")
        curobj =  self.conn.execute(f'SELECT * FROM data WHERE date ==?', (strTime,))
        return [each for each in curobj]

    def run(self, query):
        self.conn.execute(query)


class StopWatch(QtCore.QThread):
    timeConsumed = QtCore.Signal(str)
    timeSeconds = QtCore.Signal(int)
    recordSave = QtCore.Signal(int)

    def handler(self, useAI=False, AIQuality=14, time_=0):
        self.cascPath = "classifier.xml"
        self.Consumed_Time = time_
        self.useAI = useAI
        self.AIQuality = AIQuality
        self.LOOPCTRL = True
        self.start()

    def stopSafe(self):
        print("Stopping Safely")
        self.LOOPCTRL = False

    def run(self): 
        if self.useAI is True:
            pass
            # faceCascade = cv2.CascadeClassifier(self.cascPath)
            # video_capture = cv2.VideoCapture(0)
            # backend = video_capture.get(cv2.CAP_PROP_BACKEND)
            # # Check if the camera is virtual
            # if backend == "dshow" or backend == "v4l2" or backend == 700.0:
            #     print("Virtual camera detected")
            # else:
            #     print("Physical camera detected")
            #     while self.LOOPCTRL:
            #         ret, frame = video_capture.read()
            #         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            #         faces = faceCascade.detectMultiScale(
            #             gray,
            #             scaleFactor=1.1,
            #             minNeighbors=self.AIQuality,
            #             minSize=(70, 70),
            #             flags=cv2.CASCADE_SCALE_IMAGE
            #         )
            #         if (len(faces) != 0):
            #             for (x, y, w, h) in faces:
            #                 cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            #             time.sleep(0.8)
            #             elapsed_time = 1
            #             self.Consumed_Time = self.Consumed_Time + elapsed_time
            #             value = self.convert_to_FMT_AP(self.Consumed_Time)
            #             self.recordSave.emit(self.Consumed_Time)
            #             self.timeConsumed.emit(value)
            #             self.timeSeconds.emit(self.Consumed_Time)
            # video_capture.release()
        else:
            while self.LOOPCTRL:
                if self.LOOPCTRL is False:
                    break
                time.sleep(1)
                elapsed_time = 1
                self.Consumed_Time = self.Consumed_Time + elapsed_time
                value = self.convert_to_FMT_AP(self.Consumed_Time)
                self.recordSave.emit(self.Consumed_Time)
                self.timeConsumed.emit(value)
                self.timeSeconds.emit(self.Consumed_Time)

    def convert_to_FMT_AP(self, total_seconds):
        hours = int((total_seconds//3600).__round__(0))
        minutes = int(((total_seconds%3600)//60).__round__(0))
        seconds = int(((total_seconds%3600)%60).__round__(0))
        if hours < 10:
            hours = f'0{hours}'
        if minutes < 10:
            minutes = f'0{minutes}'
        if seconds < 10:
            seconds = f'0{seconds}'
        return f"{hours}:{minutes}:{seconds}"


class S_MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.resize(80, 80)
        self.move(0, 0)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
    
    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.offset = event.pos()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            new_pos = event.globalPos()
            self.move(new_pos - self.offset)


class Time_Tracker(object):
    def setupUi(self, MainWindow, use_ai, use_cache, settings_file):
        self.useAI_ = use_ai
        self.useCache = use_cache
        self.settingsFile = settings_file
        self.MainWindow = MainWindow
        self.Settings__ = self.loadSettings(self.settingsFile)
        self.centralwidget = QtWidgets.QWidget(self.MainWindow)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setAttribute(Qt.WA_TranslucentBackground, True)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        self.timeLabelStopWatch = QtWidgets.QLabel(self.frame)
        self.timeLabelStopWatch.setLayoutDirection(QtCore.Qt.LeftToRight)
        if self.Settings__ != None:
            try:
                self.timeLabelStopWatch.setStyleSheet(f"font: {self.Settings__['size']}pt \"{self.Settings__['textFamily']}\";")
            except KeyError:
                self.timeLabelStopWatch.setStyleSheet(f"font: 24pt \"Segoe UI Variable\";")
        else:
            self.timeLabelStopWatch.setStyleSheet("font: 24pt \"Segoe UI Variable\";")
        self.timeLabelStopWatch.setAttribute(Qt.WA_TranslucentBackground, True)
        self.timeLabelStopWatch.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout_2.addWidget(self.timeLabelStopWatch)
        self.verticalLayout.addWidget(self.frame)
        self.ControlLayout = QtWidgets.QGridLayout()
        self.StartStop = QtWidgets.QPushButton(self.centralwidget)
        self.StartStop.setMinimumSize(QtCore.QSize(20, 20))
        if self.Settings__ != None:
            style = '''
                QPushButton {
                    background-color: $Normal;
                    border:None;
                }
                QPushButton:hover {
                    background-color: $Hover;
                    border:None;
                }'''.replace("$Normal", self.Settings__["playbtn"]).replace("$Hover", self.Settings__["playbtnHover"])
            self.StartStop.setStyleSheet(style)
        else:
            self.StartStop.setStyleSheet('''
                                    QPushButton {
                                        background-color: rgb(20, 206, 33);
                                        border:None;
                                    }
                                    QPushButton:hover {
                                        background-color: rgb(20, 237, 37);
                                        border:None;
                                    }''')
        self.ControlLayout.addWidget(self.StartStop, 0, 1, 1, 1)
        self.Exit = QtWidgets.QPushButton(self.centralwidget)
        self.Exit.setMaximumSize(QtCore.QSize(20, 20))
        if self.Settings__ != None:
            style = '''
                QPushButton {
                    background-color: $Normal;
                    border:None;
                }
                QPushButton:hover {
                    background-color: $Hover;
                    border:None;
                }'''.replace("$Normal", self.Settings__["exitbtn"]).replace("$Hover", self.Settings__["exitbtnHover"])
            self.Exit.setStyleSheet(style)
        else:
            self.Exit.setStyleSheet('''QPushButton {
                                                    background-color: rgba(100, 0, 0);
                                                    border:None;
                                            }
                                            QPushButton:hover {
                                                    background-color: rgb(170, 0, 0);
                                                    border:None;
                                            }''')
        self.ControlLayout.addWidget(self.Exit, 0, 2, 1, 1)
        self.verticalLayout.addLayout(self.ControlLayout)
        self.MainWindow.setCentralWidget(self.centralwidget)
        self.TotalTime = 0 # Total Time in Seconds that was spent during detection
        self.StopWatchObj = StopWatch()
        self.StopWatchObj.timeConsumed.connect(self.ontimeUpdate)
        self.StopWatchObj.timeSeconds.connect(self.onPauseTime)
        self.StopWatchObj.recordSave.connect(self.saveRecord)
        if self.Settings__ != None:
            self.Storageobj = Storage(self.Settings__["storename"])
        else:
            self.Storageobj = Storage()
        self.loadRecord()
        self.commands()
        self.retranslateUi(MainWindow)
        self.startup()
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def loadSettings(self, path):
        import json, os
        self.MainWindow.setStyleSheet("background-color: rgba(59, 59, 59, 50);color: rgb(255, 255, 255);")
        if path != None:
            if os.path.exists(path) is True:
                with open(path, "r") as file_:
                    self.Settings__ = json.loads(file_.read())
                    self.MainWindow.setStyleSheet(f"background-color:{self.Settings__['background']};color:{self.Settings__['color']};")
                    return self.Settings__
            else:
                defaults = {
                                'background': 'rgba(100, 100, 150, 40)',
                                'color': 'rgb(255, 255, 255)',
                                'size': 30,
                                'playbtn': 'rgb(80, 206, 33)',
                                'playbtnHover': 'rgb(80, 237, 37)',
                                'pausebtn': 'rgb(216, 193, 17)',
                                'pausebtnHover': 'rgb(237, 212, 23)',
                                'exitbtn': 'rgb(100, 0, 0)',
                                'exitbtnHover': 'rgb(170, 0, 0)',
                                'textColor': 'rgb(255, 255, 255)',
                                'storename': 'logging.db',
                                'textFamily':'Segoe UI Variable',
                                'AIQ':9
                            }
                with open("settings.json", "w") as default_settings:
                    json.dump(defaults, default_settings)
                    print("Settings JSON file created")
                return None
        else:
            return None

    def startup(self):
        value = self.convert_to_FMT_AP(self.TotalTime)
        self.timeLabelStopWatch.setText(value)

    def convert_to_FMT_AP(self, total_seconds):
        hours = int((total_seconds//3600).__round__(0))
        minutes = int(((total_seconds%3600)//60).__round__(0))
        seconds = int(((total_seconds%3600)%60).__round__(0))
        if hours < 10:
            hours = f'0{hours}'
        if minutes < 10:
            minutes = f'0{minutes}'
        if seconds < 10:
            seconds = f'0{seconds}'
        return f"{hours}:{minutes}:{seconds}"

    def ontimeUpdate(self, value):
        self.timeLabelStopWatch.setText(value)
    
    def onPauseTime(self, seconds):
        print(seconds)
        self.TotalTime = seconds
    
    def loadRecord(self):
        year_ = datetime.now().year
        month_ = datetime.now().month
        day_ = datetime.now().day
        try:
            self.TotalTime = self.Storageobj.getSpecific(year_, month_, day_)[0][1]
            print("Total Time Loaded from DB",self.TotalTime)
        except Exception:
            self.TotalTime = 0
    
    def saveRecord(self, value):
        year_ = datetime.now().year
        month_ = datetime.now().month
        day_ = datetime.now().day
        self.Storageobj.record(year_, month_, day_, value)

    def commands(self):
        self.StartStop.clicked.connect(self.OnStart)
        self.Exit.clicked.connect(self.OnExit)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.timeLabelStopWatch.setText(_translate("MainWindow", "00:00:00"))
        self.StartStop.setText(_translate("MainWindow", "Start"))
        self.Exit.setText(_translate("MainWindow", "X"))

    def OnStart(self):
        if self.StopWatchObj.isRunning() is False:
            if self.Settings__ != None:
                style = '''
                    QPushButton {
                        background-color: $Normal;
                        border:None;
                    }
                    QPushButton:hover {
                        background-color: $Hover;
                        border:None;
                    }'''.replace("$Normal", self.Settings__["pausebtn"]).replace("$Hover", self.Settings__["pausebtnHover"])
                self.StopWatchObj.handler(useAI=self.useAI_, AIQuality=self.Settings__["AIQ"],time_=self.TotalTime)
                self.StartStop.setStyleSheet(style)
            else:
                self.StartStop.setStyleSheet('''
                                    QPushButton {
                                        background-color: rgb(216, 193, 17);
                                        border:None;
                                    }
                                    QPushButton:hover {
                                        background-color: rgb(237, 212, 23);
                                        border:None;
                                    }''')
                self.StopWatchObj.handler(useAI=self.useAI_, time_=self.TotalTime)
            self.StartStop.setText("Pause")
        else:
            self.StopWatchObj.stopSafe()
            self.StopWatchObj.terminate()
            if self.Settings__ != None:
                style = '''
                    QPushButton {
                        background-color: $Normal;
                        border:None;
                    }
                    QPushButton:hover {
                        background-color: $Hover;
                        border:None;
                    }'''.replace("$Normal", self.Settings__["playbtn"]).replace("$Hover", self.Settings__["playbtnHover"])
                self.StartStop.setStyleSheet(style)
            else:
                self.StartStop.setStyleSheet('''
                                        QPushButton {
                                            background-color: rgb(20, 206, 33);
                                            border:None;
                                        }
                                        QPushButton:hover {
                                            background-color: rgb(20, 237, 37);
                                            border:None;
                                        }''')

    def OnExit(self):
        if self.StopWatchObj.isRunning() is True:
            self.StopWatchObj.stopSafe()
            self.StopWatchObj.terminate()
            self.MainWindow.close()
        else:
            self.MainWindow.close()


if __name__ == "__main__":
    import sys
    import argparse

    # Create a new ArgumentParser object
    parser = argparse.ArgumentParser(description='Description of your script.')

    # Add arguments
    #parser.add_argument('--AI', action='store_true', help='Use AI to perform the task.')
    #parser.add_argument('--size', type=int, help='A value used for setting size of the widget')
    parser.add_argument('--settings', default="settings.json" , help='Specify settings file location.')
    parser.add_argument('--nocache', action='store_true', help='Do not use cached data.')

    # Parse arguments
    args = parser.parse_args()

    # Access parsed arguments
    use_ai = False
    settings_file = args.settings
    use_cache = not args.nocache

    app = QtWidgets.QApplication(sys.argv)
    MW_obj = S_MainWindow()
    timetracker_obj = Time_Tracker()
    timetracker_obj.setupUi(MW_obj, use_ai, use_cache, settings_file)
    MW_obj.show()
    sys.exit(app.exec_())
