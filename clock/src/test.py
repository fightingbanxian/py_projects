import sys
import os
import ntplib
import time
import win32api

from datetime import datetime

from PySide2.QtWidgets import QWidget, QApplication, QMessageBox
from PySide2.QtCore import Slot, Qt
from PySide2.QtCore import QPoint
from PySide2.QtCore import QTimerEvent
from PySide2.QtGui import QPaintEvent, QPainter, QColor, QValidator, QIntValidator

from ui_main import Ui_Form

import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


class AnalogClock(QWidget):

    def __init__(self, parent):
        super(AnalogClock, self).__init__(parent)

        now = datetime.now()
        self._hour = now.hour
        self._minute = now.minute
        self._second = now.second

    @property
    def hour(self) -> int:
        return self._hour

    @property
    def minute(self) -> int:
        return self._minute

    @property
    def second(self) -> int:
        return self._second

    @hour.setter
    def hour(self, h: int):
        self._hour = h
        self.update()

    @minute.setter
    def minute(self, m: int):
        self._minute = m
        self.update()

    @second.setter
    def second(self, s: int):
        self._second = s
        self.update()

    @property
    def time(self):
        return self._hour, self._minute, self._second

    @time.setter
    def time(self, t: tuple):
        self._hour, self._minute, self._second = t
        self.update()

    def paintEvent(self, event):
        hour_hand = [QPoint(7, 8), QPoint(-7, 8), QPoint(0, -40)]
        minute_hand = [QPoint(7, 8), QPoint(-7, 8), QPoint(0, -70)]
        second_hand = [QPoint(2, 8), QPoint(-2, 8), QPoint(0, -90)]

        hour_color = QColor(0x8b, 0, 0xff)
        minute_color = QColor(0, 0xbf, 0xff, 191)
        second_color = QColor(0xff, 0x82, 0xab, 191)

        side = min(self.width(), self.height())

        painter = QPainter(self)

        # pre settings

        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)

        painter.scale(side / 200, side / 200)

        painter.setPen(Qt.NoPen)

        # draw hour scale & hour hand
        painter.setBrush(hour_color)

        painter.save()

        painter.rotate(30 * (self._hour + self._minute / 60))
        painter.drawConvexPolygon(hour_hand)
        painter.restore()

        painter.setPen(hour_color)

        for i in range(12):
            painter.drawLine(88, 0, 96, 0)
            painter.rotate(30)

        painter.setPen(Qt.NoPen)

        # draw minute scale & minute hand
        painter.setBrush(minute_color)

        painter.save()

        painter.rotate(6 * (self._minute + self._second / 60))
        painter.drawConvexPolygon(minute_hand)
        painter.restore()

        painter.setPen(minute_color)

        for i in range(60):
            if i % 5:
                painter.drawLine(92, 0, 96, 0)
            painter.rotate(6.0)

        painter.setPen(Qt.NoPen)

        # draw second scale & second hand
        painter.setBrush(second_color)

        painter.save()

        painter.rotate(6 * self._second)
        painter.drawConvexPolygon(second_hand)
        painter.restore()


class Cal(QWidget):

    HS = "甲乙丙丁戊己庚辛壬癸"
    EB = "子丑寅卯辰巳午未申酉戌亥"
    ZD = "鼠牛虎兔龙蛇马羊猴鸡狗猪"

    def __init__(self, admin):
        super(Cal, self).__init__()

        self.ui = Ui_Form()

        self.ui.setupUi(self)

        self.clock = AnalogClock(self)
        self.clock.setFixedWidth(200)
        self.clock.setFixedHeight(200)
        self.clock.setObjectName('clock')
        self.ui.horizontalLayout_4.addWidget(self.clock)

        self.lock()

        self._datetime = datetime.now()

        self.updateDatetime()

        self.timer_id = self.startTimer(1000)

        self.admin = admin

        self.editing = False
        if admin:
            self.ui.edit_button.clicked.connect(self.onEditButtonClicked)
            self.ui.fix_button.clicked.connect(self.onFixButtonClicked)
        else:
            self.ui.edit_button.setDisabled(True)
            self.ui.fix_button.setDisabled(True)

        self.year_validator = QIntValidator(0, 99999, self)
        self.month_validator = QIntValidator(1, 12, self)
        self.day_validator = QIntValidator(1, 30, self)
        self.setDayValidator()

        self.hour_validator = QIntValidator(0, 23, self)
        self.time_validator = QIntValidator(0, 59, self)

        self.ui.year_edit.setValidator(self.year_validator)
        self.ui.month_edit.setValidator(self.month_validator)
        self.ui.day_edit.setValidator(self.day_validator)

        self.ui.hour_edit.setValidator(self.hour_validator)
        self.ui.minute_edit.setValidator(self.time_validator)
        self.ui.second_edit.setValidator(self.time_validator)

        self.ui.year_edit.textChanged.connect(self.onYearChanged)
        self.ui.month_edit.textChanged.connect(self.onMonthChanged)
        self.ui.day_edit.textChanged.connect(self.onDayChanged)

        self.ui.hour_edit.textChanged.connect(self.onHourChanged)
        self.ui.minute_edit.textChanged.connect(self.onMinuteChanged)
        self.ui.second_edit.textChanged.connect(self.onSecondChanged)


    # lock lineEdit
    def lock(self):
        self.ui.year_edit.setReadOnly(True)
        self.ui.month_edit.setReadOnly(True)
        self.ui.day_edit.setReadOnly(True)

        self.ui.hour_edit.setReadOnly(True)
        self.ui.minute_edit.setReadOnly(True)
        self.ui.second_edit.setReadOnly(True)

    # unlock lineEdit
    def unlock(self):
        self.ui.year_edit.setReadOnly(False)
        self.ui.month_edit.setReadOnly(False)
        self.ui.day_edit.setReadOnly(False)

        self.ui.hour_edit.setReadOnly(False)
        self.ui.minute_edit.setReadOnly(False)
        self.ui.second_edit.setReadOnly(False)

    @property
    def time(self):
        return self._datetime

    @time.setter
    def time(self, dtime: datetime):
        self._datetime = dtime
        self.updateDatetime()

    def isLeapYear(self):
        year = self._datetime.year
        if year % 100 == 0 and year % 400 != 0:
            return False, "平年"
        elif year % 4 != 0:
            return False, "平年"
        return True, "闰年"

    def calcInfo(self):
        # 天干
        hs = self.HS[(self._datetime.year - 4) % 10]
        # 地支
        eb = self.EB[(self._datetime.year - 4) % 12]
        # 属相
        zd = self.ZD[(self._datetime.year - 4) % 12]
        self.ui.lbl_info.setText("{}{}{}年 {}".format(hs, eb, zd, self.isLeapYear()[1]))

    def dt2t(self, dtime: datetime):
        tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec, tm_wday, tm_yday, tm_isdst = time.gmtime(dtime.timestamp())
        return tm_year, tm_mon, tm_wday, tm_mday, tm_hour, tm_min, tm_sec, 0

    def ts2t(self, timestamp: int):
        tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec, tm_wday, tm_yday, tm_isdst = time.gmtime(timestamp)
        return tm_year, tm_mon, tm_wday, tm_mday, tm_hour, tm_min, tm_sec, 0

    def onFixButtonClicked(self):
        try:
            c = ntplib.NTPClient()
            res = c.request('pool.ntp.org')
            win32api.SetSystemTime(*self.ts2t(res.tx_time))
            if self.editing:
                self.ui.edit_button.click()
        except:
            pass

    def onEditButtonClicked(self):
        self.editing = not self.editing
        self.ui.edit_button.setStyleSheet("background: rgb(0, 0, 233); color: rgb(255, 255, 255)" if self.editing
                                          else "")
        if self.editing:
            self.unlock()
            try:
                win32api.SetSystemTime(*self.dt2t(self._datetime))
            except:
                # set failed
                self.editing = False
                self.ui.edit_button.setStyleSheet("")
                self.lock()
        else:
            self.lock()

    def setDayValidator(self):
        month = self._datetime.month
        if month == 2:
            if self.isLeapYear()[0]:
                self.day_validator.setTop(29)
            else:
                self.day_validator.setTop(28)
        elif month in [1, 3, 5, 7, 8, 10, 12]:
            self.day_validator.setTop(31)
        else:
            self.day_validator.setTop(30)

    def onYearChanged(self, year):
        if not self.editing:
            return
        year = int(0 if year == '' else year)
        try:
            self._datetime = self._datetime.replace(year=year)
            self.setDayValidator()
            self.calcInfo()
            win32api.SetSystemTime(*self.dt2t(self._datetime))
        except:
            pass

    def onMonthChanged(self, month):
        if not self.editing:
            return
        month = int(0 if month == '' else month)
        try:
            self._datetime = self._datetime.replace(month=month)
            self.setDayValidator()
            win32api.SetSystemTime(*self.dt2t(self._datetime))
        except:
            pass

    def onDayChanged(self, day):
        if not self.editing:
            return
        try:
            day = int(0 if day == '' else day)
            self._datetime = self._datetime.replace(day=day)
            win32api.SetSystemTime(*self.dt2t(self._datetime))
        except:
            pass

    def onHourChanged(self, hour):
        if not self.editing:
            return
        hour = int(0 if hour == '' else hour)
        try:
            self._datetime = self._datetime.replace(hour=hour)
            self.clock.hour = hour
            win32api.SetSystemTime(*self.dt2t(self._datetime))
        except:
            pass

    def onMinuteChanged(self, minute):
        if not self.editing:
            return
        minute = int(0 if minute == '' else minute)
        try:
            self._datetime = self._datetime.replace(minute=minute)
            self.clock.minute = minute
            win32api.SetSystemTime(*self.dt2t(self._datetime))
        except:
            pass

    def onSecondChanged(self, second):
        if not self.editing:
            return
        second = int(0 if second == '' else second)
        try:
            self._datetime = self._datetime.replace(second=second)
            self.clock.second = second
            win32api.SetSystemTime(*self.dt2t(self._datetime))
        except:
            pass

    def updateDatetime(self):
        self.ui.year_edit.setText(str(self._datetime.year))
        self.ui.month_edit.setText(str(self._datetime.month))
        self.ui.day_edit.setText(str(self._datetime.day))

        self.ui.hour_edit.setText(str(self._datetime.hour))
        self.ui.minute_edit.setText(str(self._datetime.minute))
        self.ui.second_edit.setText(str(self._datetime.second))

        self.clock.time = (self._datetime.hour, self._datetime.minute, self._datetime.second)
        self.calcInfo()

    def timerEvent(self, event: QTimerEvent):
        if event.timerId() == self.timer_id and self.editing is False:
            self.time = datetime.now()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    if not is_admin():
        msg_box = QMessageBox()
        msg_box.setText("程序需要申请管理员权限来更改您的系统时间")
        msg_box.setInformativeText("是否同意?")
        msg_box.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        ret = msg_box.exec_()
        if ret == QMessageBox.Yes:
            sys.exit(ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1))
        else:
            calendar = Cal(False)
            calendar.show()
            sys.exit(app.exec_())
    else:
        msg_box = QMessageBox()
        msg_box.setText("'调整'和'校准'功能会修改您的系统时间，请注意")
        msg_box.exec_()
        calendar = Cal(True)
        calendar.show()
        sys.exit(app.exec_())
