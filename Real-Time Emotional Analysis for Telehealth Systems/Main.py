import sys
import random
import datetime, time
import math

import matplotlib.pyplot as plt
import csv

import pyautogui
import cv2
from deepface import DeepFace
import numpy as np

import pandas as pd

from threading import Thread
from PyQt5 import QtGui, QtCore, uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPixmap, QPainter, QFont
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

global rec, out, dfRes
rec = 0

#variables for DF analysis
angryArray = []
disgustArray = []
fearArray = []
happyArray = []
sadArray = []
surpriseArray = []
neutralArray = []

resultDict = {'angry': angryArray, 'disgust': disgustArray, 'fear': fearArray, 'happy': happyArray, 'sad': sadArray, 'surprise': surpriseArray, 'neutral': neutralArray}

EMOTION_NAMEES = ["Angry\t", "Disgust\t", "Fear\t", "Happy\t", "Sad\t", "Surprise ", "Neutral\t"]
EMOTION_COLORS = ["red", "green", "pink", "lime", "blue", "orange", "white"]



def dfthread():
    global rec
    attributes = ['emotion']
    EMOTION_NAMES = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]
    while rec:

        time.sleep(0.75)

        sc1 = pyautogui.screenshot()
        sc1 = np.array(sc1)
        sc1 = sc1[:, :, ::-1].copy()
        sc1 = sc1[285:800, 10:955, ::-1].copy()
        obj = DeepFace.analyze(sc1, attributes, enforce_detection=False)
        arr = [obj[0]['emotion'][EMOTION_NAMES[i]] for i in range(7)]
        mywindow.set_emo_widget_state(arr)
        resultDict['angry'].append(float(obj[0]['emotion']['angry']))
        resultDict['disgust'].append(float(obj[0]['emotion']['disgust']))
        resultDict['fear'].append(float(obj[0]['emotion']['fear']))
        resultDict['happy'].append(float(obj[0]['emotion']['happy']))
        resultDict['sad'].append(float(obj[0]['emotion']['sad']))
        resultDict['surprise'].append(float(obj[0]['emotion']['surprise']))
        resultDict['neutral'].append(float(obj[0]['emotion']['neutral']))

    arr = np.asarray([resultDict[EMOTION_NAMES[0]],resultDict[EMOTION_NAMES[1]],resultDict[EMOTION_NAMES[2]],resultDict[EMOTION_NAMES[3]],resultDict[EMOTION_NAMES[4]],resultDict[EMOTION_NAMES[5]],resultDict[EMOTION_NAMES[6]]])
    pd.DataFrame(arr).to_csv('UserData//emotions.csv', header=None, index=None)
    out.release()
    print_plot()


def df(out):
    global rec
    while rec:
        init = time.perf_counter()
        sc = pyautogui.screenshot()
        sc = np.array(sc)
        sc = sc[:, :, ::-1].copy()
        out.write(sc)
        fin = time.perf_counter()
        # print(sc.shape)
        # cv2.imshow("original", sc1)
        # print(fin-init)
        time.sleep(0.066-min([(fin-init), 0.066]))
        # time.sleep(0.05)


def print_plot():
    csvFile = "UserData//emotions.csv"

    with open(csvFile) as csvfile:
        reader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)

        row1 = next(reader)
        angryData = row1

        row2 = next(reader)
        disgustData = row2

        row3 = next(reader)
        fearData = row3

        row4 = next(reader)
        happyData = row4

        row5 = next(reader)
        sadData = row5

        row6 = next(reader)
        surpriseData = row6

        row7 = next(reader)
        neutralData = row7

    time = np.arange(0, len(angryData))

    plt.title(label="Emotions v. Time")
    plt.xlabel("Time in s")
    plt.ylabel("Emotion %")
    plt.plot(time, angryData, label="Anger", linestyle="-.", color="red")
    plt.plot(time, disgustData, label="Disgust", linestyle="-.", color='green')
    plt.plot(time, fearData, label="Fear", linestyle="-.", color='pink')
    plt.plot(time, happyData, label="Happy", linestyle="-.", color='lime')
    plt.plot(time, sadData, label="Sad", linestyle="-.", color='blue')
    plt.plot(time, surpriseData, label="Surprise", linestyle="-.", color='orange')
    plt.plot(time, neutralData, label="Neutral", linestyle="-.", color='grey')
    plt.legend()
    plt.savefig('UserData//graph.png', bbox_inches='tight')

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.X11BypassWindowManagerHint
        )
        self.setGeometry(
            QtWidgets.QStyle.alignedRect(
                QtCore.Qt.LeftToRight, QtCore.Qt.AlignRight,
                QtCore.QSize(500, 500),
                QtWidgets.qApp.desktop().availableGeometry()
        ))

        self.emoWidget = QLabel("", self)

        self.emoWidget.setAlignment(Qt.AlignLeft)
        font = self.emoWidget.font()
        font.setPointSize(12)
        self.emoWidget.setStyleSheet("color: white;")
        self.emoWidget.setFont(QFont("Courier New",12))
        self.emoWidget.adjustSize()
        self.emoWidget.opacity_effect = QGraphicsOpacityEffect()
        self.emoWidget.move(340, 100)

        self.startWidget = QLabel(self)
        startPixmap = QPixmap("Assets//play_button.png")
        self.startWidget.setPixmap(startPixmap)
        self.startWidget.move(440, 155)
        self.startWidget.adjustSize()
        self.startWidget.setScaledContents(True)
        self.startWidget.resize(30, 30)
        self.startWidget.isStart = True
        self.startWidget.mousePressEvent = self.start_widget_clicked
    # Emotions: Angry, Disgust, Fear, Happy, Sad, Surprise, Neutral

    def set_emo_widget_state(self, array):
        value = max(array)
        value2 = sorted(array)[5]
        emotion = array.index(value)
        emotion2 = array.index(value2)
        self.emoWidget.setText(EMOTION_NAMEES[emotion]+str(int(value))+"%"+"\n"+EMOTION_NAMEES[emotion2]+str(int(value2))+"%")
        self.emoWidget.adjustSize()
        # THE FOLLOWING LINE OF CODE JUST BREAKS YOUR COMPUTER I HAVE NO CLUE WHYYYYYY
        # self.emoWidget.setStyleSheet("color: "+str(EMOTION_COLORS[emotion])+";")
        self.emoWidget.opacity_effect.setOpacity(.3+.7*value/100.0)
        self.emoWidget.setGraphicsEffect(self.emoWidget.opacity_effect)

    def start_widget_clicked(self, event):
        global rec
        if self.startWidget.isStart:
            self.startWidget.isStart = False
            self.set_start_widget_stop()
        else:
            self.set_start_widget_start()

    def set_start_widget_stop(self):
        global rec, out
        stopPixmap = QPixmap("Assets//stop_button.png")
        self.startWidget.setPixmap(stopPixmap)
        rec = not rec
        now = datetime.datetime.now()
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        # change frame size
        out = cv2.VideoWriter('UserData//recording_{}.avi'.format(str(now).replace(":", '')), fourcc, 15.0, (1920, 1080))
        # Start new thread for recording the video
        thread = Thread(target=df, args=[out, ])
        thread.start()
        threaddf = Thread(target=dfthread, args=[ ])
        threaddf.start()



    def set_start_widget_start(self):
        global rec, out
        rec = not rec
        # print_plot()
        QtWidgets.qApp.quit()



    # def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
    #     self.set_emo_widget_state(random.randint(0, 6), random.random()*100)

        # QtWidgets.qApp.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = MainWindow()
    mywindow.setWindowOpacity(0.8)


    # layout = QHBoxLayout(mywindow)
    #
    # button = PicButton(QPixmap("image.png"))
    # layout.addWidget(button)


    mywindow.show()
    app.exec_()