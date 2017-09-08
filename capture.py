import cv2
import time
import wx
import random

seconds_to_prepare = 2
seconds_to_close = 10
label_filename = "labels.csv"
ball_size = 16

class MainWindow(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        self.cap = cv2.VideoCapture(-1)
        if not self.cap.isOpened():
            self.Close()

        w, h = wx.GetDisplaySize()
        self.ballPosition = [random.randint(0, w), random.randint(0, h)] # [w, h]
        self.lastPosition = None
        self.ballDelta = [1, 1]

        self.label_file = open(label_filename, "a")

        self.move_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.move, self.move_timer)
        self.move_timer.Start(20)

        self.start_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.start_capturing, self.start_timer)
        self.start_timer.Start(seconds_to_prepare * 1000)

    def start_capturing(self, event):
        self.start_timer.Stop()

        self.capture_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.capture, self.capture_timer)
        self.capture_timer.Start(100)

        self.close_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.close, self.close_timer)
        self.close_timer.Start(seconds_to_close * 1000)

    def close(self, event):
        self.label_file.close()
        self.Close()

    def move(self, event):
        self.ballPosition[0] += self.ballDelta[0]
        self.ballPosition[1] += self.ballDelta[1]
        w, h = wx.DisplaySize()
        if self.ballPosition[0] > w:
            self.ballPosition[0] = w
            self.ballDelta[0] *= -1
        if self.ballPosition[1] > h:
            self.ballPosition[1] = h
            self.ballDelta[1] *= -1
        if self.ballPosition[0] < 0:
            self.ballPosition[0] = 0
            self.ballDelta[0] *= -1
        if self.ballPosition[1] < 0:
            self.ballPosition[1] = 0
            self.ballDelta[1] *= -1

        dc = wx.ScreenDC()
        dc.StartDrawingOnTop()
        dc.SetLogicalFunction(wx.XOR)
        if self.lastPosition is not None:
            dc.DrawRectangle(self.lastPosition[0], self.lastPosition[1], ball_size, ball_size)
        self.lastPosition = (self.ballPosition[0] - ball_size / 2, self.ballPosition[1] - ball_size / 2)
        dc.DrawRectangle(self.lastPosition[0], self.lastPosition[1], ball_size, ball_size)
        dc.EndDrawingOnTop()

    def capture(self, event):
        ret, frame = self.cap.read()
        if not ret:
            return

        filename = str(int(time.time() * 1000.0)) + ".jpg"
        cv2.imwrite(filename, frame)
        self.label_file.write(filename + "," + str(self.ballPosition[0]) + "," + str(self.ballPosition[1]) + "\n")

app = wx.App(False)
win = MainWindow(None)
app.MainLoop()
