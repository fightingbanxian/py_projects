import sys

import decimal
from decimal import Decimal

import math
import random

from PySide2.QtWidgets import QMainWindow, QApplication, QPushButton
from PySide2.QtCore import Slot, Qt
from PySide2.QtGui import QKeyEvent

from ui_mainwindow import Ui_MainWindow


class MainWin(QMainWindow):
    def __init__(self):
        super(MainWin, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # bind exit menu
        self.ui.menu_file.triggered.connect(lambda x: sys.exit())

        # num keys
        self.ui.btngrp_n_nums.buttonClicked.connect(self.number_input)
        self.ui.btngrp_s_nums.buttonClicked.connect(self.number_input)

        # CE
        self.ui.btn_n_ce.clicked.connect(self.clear_entry)
        self.ui.btn_s_ce.clicked.connect(self.clear_entry)

        # C
        self.ui.btn_n_c.clicked.connect(self.clear_all)
        self.ui.btn_s_c.clicked.connect(self.clear_all)

        # backspace
        self.ui.btn_n_backspace.clicked.connect(self.backspace)
        self.ui.btn_s_backspace.clicked.connect(self.backspace)

        # inverse
        self.ui.btn_n_inv.clicked.connect(self.inverse)
        self.ui.btn_s_inv.clicked.connect(self.inverse)

        # dot
        self.ui.btn_n_dot.clicked.connect(self.dot)
        self.ui.btn_s_dot.clicked.connect(self.dot)

        # percent
        self.ui.btn_n_percent.clicked.connect(self.percent)

        # rec
        self.ui.btn_n_rec.clicked.connect(self.rec)
        self.ui.btn_s_rec.clicked.connect(self.rec)

        # sqrt
        self.ui.btn_n_sqrt.clicked.connect(self.sqrt)
        self.ui.btn_s_sqrt.clicked.connect(self.sqrt)

        # cube
        self.ui.btn_n_cube.clicked.connect(self.cube)
        self.ui.btn_s_cube.clicked.connect(self.cube)

        # square
        self.ui.btn_n_square.clicked.connect(self.sqr)
        self.ui.btn_s_square.clicked.connect(self.sqr)

        # add
        self.ui.btn_n_add.clicked.connect(self.add)
        self.ui.btn_s_add.clicked.connect(self.add)

        # sub
        self.ui.btn_n_sub.clicked.connect(self.sub)
        self.ui.btn_s_sub.clicked.connect(self.sub)

        # mul
        self.ui.btn_n_mul.clicked.connect(self.mul)
        self.ui.btn_s_mul.clicked.connect(self.mul)

        # div
        self.ui.btn_n_div.clicked.connect(self.div)
        self.ui.btn_s_div.clicked.connect(self.div)

        # eql
        self.ui.btn_n_eql.clicked.connect(self.enter)
        self.ui.btn_s_eql.clicked.connect(self.enter)

        # pow
        self.ui.btn_s_pow.clicked.connect(self.pow)

        # yroot
        self.ui.btn_s_sqrtx.clicked.connect(self.yroot)

        # 10x
        self.ui.btn_s_10x.clicked.connect(self._10x)

        # ex
        self.ui.btn_s_ex.clicked.connect(self.ex)

        # pi
        self.ui.btn_s_pi.clicked.connect(self.pi)

        # rand
        self.ui.btn_s_rand.clicked.connect(self.rand)

        # deg
        self.ui.btn_s_deg.clicked.connect(self.deg)

        # hyp
        self.ui.btn_s_hyp.clicked.connect(self.hyp)

        # log10
        self.ui.btn_s_log.clicked.connect(self.log10)

        # ln
        self.ui.btn_s_ln.clicked.connect(self.ln)

        # fact
        self.ui.btn_s_fact.clicked.connect(self.fact)

        # mod
        self.ui.btn_s_mod.clicked.connect(self.mod)

        # logab
        self.ui.btn_s_logab.clicked.connect(self.logab)

        # P
        self.ui.btn_s_perm.clicked.connect(self.perm)

        # C
        self.ui.btn_s_comb.clicked.connect(self.comb)

        # sin
        self.ui.btn_s_sin.clicked.connect(self.sin)

        # cos
        self.ui.btn_s_cos.clicked.connect(self.cos)

        # tan
        self.ui.btn_s_tan.clicked.connect(self.tan)

        # asin
        self.ui.btn_s_asin.clicked.connect(self.asin)

        # acos
        self.ui.btn_s_acos.clicked.connect(self.acos)

        # atan
        self.ui.btn_s_atan.clicked.connect(self.atan)

        # (
        self.ui.btn_s_bra.clicked.connect(self.bra)

        # )
        self.ui.btn_s_ket.clicked.connect(self.ket)

        # status variables
        self.clear_numbers = False
        self.error = False
        self.newnum_inputed = False
        self.brackets = 0

        # last status
        self.num_last: Decimal = None
        self.text_last: str = None
        self.num_curr: Decimal = Decimal(0)
        self.text_curr: str = None
        self.op_cache = None

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        print(key)
        if ord('0') <= key <= ord('9'):  # 0 ~ 9
            return self.num_input(chr(key))
        elif key == 16777219:  # backspace
            return self.backspace()
        elif key == 16777220:  # enter
            return self.enter()
        elif key == ord('+'):
            return self.add()
        elif key == ord('-'):
            return self.sub()
        elif key == ord('*'):
            return self.mul()
        elif key == ord('/'):
            return self.div()
        elif key == ord('%'):
            return self.percent()
        elif key == ord('C'):
            return self.clear_all()
        elif key in (ord('E'), 16777223):  # e, delete
            return self.clear_entry()
        elif key == ord('^'):
            return self.pow()

    @property
    def numtext(self):
        return self.ui.linedit_res.text()

    @numtext.setter
    def numtext(self, string: str):
        self.ui.linedit_res.setText(string)

    @property
    def expr(self):
        return self.ui.linedit_expr.text()

    @expr.setter
    def expr(self, string: str):
        self.ui.linedit_expr.setText(string)

    def update_(self):
        self.ui.linedit_expr.update()
        self.ui.linedit_res.update()
        try:
            self.num_curr = Decimal(self.numtext)
        except:
            self.num_curr = Decimal(0)
        if self.error:
            self.unlock_keys()
            self.error = True

    def _update_expr(self):
        self.ui.linedit_expr.setText(('' if self.text_last is None else self.text_last) + \
                                     (' ' + self.op_cache + ' ' if self.op_cache is not None else '') + \
                                     ('' if self.text_curr is None else self.text_curr))
        self.ui.linedit_expr.update()

    def update_expr(self, func_name: str):
        if self.text_curr is None:
            self.text_curr = str(self.num_curr)
        self.text_curr = func_name + '(' + self.text_curr + ')'
        self._update_expr()

    def mov(self):
        if self.text_curr is None:
            self.text_last = str(self.num_curr)
        else:
            self.text_last = self.text_curr
        self.num_last = self.num_curr
        self.text_curr = None
        self.clear_numbers = True

    def prep(self, op_code: str):
        if self.op_cache is None:
            self.mov()
        else:
            if not self.newnum_inputed:
                self.op_cache = op_code
                self._update_expr()
                return
            try:
                self.num_last = self.calc(self.num_last, self.op_cache, self.num_curr)
            except decimal.DivisionByZero:
                self.errormsg('除数不能为零')
                return
            except decimal.Overflow:
                self.errormsg('溢出')
                return
            except:
                self.errormsg('无效输入')
                return
            self.text_last += ' ' + self.op_cache + ' ' + str(
                self.num_curr) if self.text_curr is None else self.text_curr
            self.numtext = str(self.num_last)
            self.clear_numbers = True
            self.op_cache = None
            self.text_curr = None

        self.op_cache = op_code
        self.update_()
        self._update_expr()
        self.newnum_inputed = False

    def calc(self, num1: Decimal, op_code: str, num2: Decimal) -> Decimal:
        if op_code == '+':
            return (num1 + num2).normalize()
        elif op_code == '×':
            return (num1 * num2).normalize()
        elif op_code == '-':
            return (num1 - num2).normalize()
        elif op_code == '÷':
            return (num1 / num2).normalize()
        elif op_code == '^':
            return (num1 ** num2).normalize()
        elif op_code == 'yroot':
            return (num1 ** (1 / num2)).normalize()
        elif op_code == 'C':
            return (self.factorial(num1) // (self.factorial(num1 - num2) * self.factorial(num2))).normalize()
        elif op_code == 'P':
            return (self.factorial(num1) // self.factorial(num1 - num2)).normalize()
        elif op_code == 'Mod':
            return (num1 % num2).normalize()
        elif op_code == 'log':
            return (num1.ln() / num2.ln()).normalize()

    def number_input(self, btn: QPushButton):
        self.newnum_inputed = True
        num = btn.text()
        if self.clear_numbers or self.numtext == '0':
            self.numtext = num
        else:
            self.numtext = self.numtext + num
        self.update_()
        self.clear_numbers = False

    def num_input(self, num: str):
        self.newnum_inputed = True
        if self.clear_numbers or self.numtext == '0':
            self.numtext = num
        else:
            self.numtext = self.numtext + num
        self.update_()
        self.clear_numbers = False

    def clear_entry(self):
        self.numtext = '0'
        self.clear_numbers = False
        self.num_curr = Decimal(0)
        self.text_curr = None
        self._update_expr()
        self.update_()

    def clear_all(self):
        self.numtext = '0'
        self.clear_numbers = False
        self.ui.linedit_expr.clear()
        self.clear_entry()
        self.num_last = None
        self.text_last = None
        self.num_curr = None
        self.text_curr = None
        self.op_cache = None
        self._update_expr()
        self.update_()

    def backspace(self):
        if self.error:
            self.clear_entry()
        string = self.numtext
        if len(string) > 2 or (not string.startswith('-') and len(string) > 1):
            self.ui.linedit_res.setText(string[:-1])
        else:
            self.numtext = '0'
        self.update_()

    def dot(self):
        if self.clear_numbers:
            self.numtext = 0
        string = self.numtext
        if '.' not in string:
            self.numtext = string + '.'
        self.update_()

    def inverse(self):
        if self.clear_numbers:
            pass
        else:
            string = self.numtext
            if string != '0':
                if string.startswith('-'):
                    self.numtext = string[1:]
                else:
                    self.numtext = '-' + string
        self.update_()

    def percent(self):
        self.numtext = str((Decimal(self.numtext) / 100).normalize())
        self.update_()

    def rec(self):
        try:
            self.update_expr('1/')
            self.numtext = str((1 / Decimal(self.numtext)).normalize())
            self.update_()
        except:
            self.errormsg("除数不能为零")

    def add(self):
        self.prep('+')

    def sub(self):
        self.prep('-')

    def mul(self):
        self.prep('×')

    def div(self):
        self.prep('÷')

    def pow(self):
        self.prep('^')

    def yroot(self):
        self.prep('yroot')

    def perm(self):
        self.prep('P')

    def comb(self):
        self.prep('C')

    def mod(self):
        self.prep('Mod')

    def logab(self):
        self.prep('log')

    def enter(self):
        if self.op_cache is not None:
            try:
                res = self.calc(self.num_last, self.op_cache, self.num_curr)
                self.numtext = str(res)
            except decimal.DivisionByZero:
                self.errormsg('除数不能为零')
                return
            except decimal.Overflow:
                self.errormsg('溢出')
                return
            except decimal.InvalidOperation:
                self.errormsg('无效输入')
                return
        self.ui.linedit_expr.clear()
        self.text_curr = None
        self.text_last = None
        self.num_last = None
        self.op_cache = None
        self.num_curr = None
        self.clear_numbers = True
        self.update_()

    def sqr(self):
        try:
            self.update_expr('sqr')
            self.numtext = str((Decimal(self.numtext) ** 2).normalize())
            self.update_()
        except decimal.Overflow:
            self.errormsg('溢出')

    def cube(self):
        try:
            self.update_expr('cube')
            self.numtext = str((Decimal(self.numtext) ** 3).normalize())
            self.update_()
        except decimal.Overflow:
            self.errormsg('溢出')

    def sqrt(self):
        try:
            self.update_expr('√')
            self.numtext = str(res)
            self.numtext = str(Decimal(self.numtext).sqrt().normalize())
            self.update_()
        except:
            self.errormsg()

    def _10x(self):
        try:
            self.update_expr('10^')
            self.numtext = str((Decimal('10') ** Decimal(self.numtext)).normalize())
            self.update_()
        except decimal.Overflow:
            self.errormsg('溢出')

    def ex(self):
        try:
            self.update_expr('e^')
            self.numtext = str((Decimal(math.e) ** Decimal(self.numtext)).normalize())
            self.update_()
        except decimal.Overflow:
            self.errormsg('溢出')

    def pi(self):
        self.numtext = str(math.pi)
        self.update_()
        self.clear_numbers = True

    def rand(self):
        self.numtext = str(random.random())
        self.update_()
        self.clear_numbers = True

    def log10(self):
        try:
            self.update_expr('log10')
            self.numtext = str(Decimal(self.numtext).log10().normalize())
            self.update_()
        except:
            self.errormsg()

    def ln(self):
        try:
            self.update_expr('ln')
            self.numtext = str(Decimal(self.numtext).ln().normalize())
            self.update_()
        except:
            self.errormsg()

    def factorial(self, num: Decimal) -> Decimal:
        if num < 0:
            self.errormsg()
            raise RuntimeError
        elif num > 100000:
            self.errormsg('溢出')
            raise RuntimeError
        elif num == 0:
            return Decimal('1')
        else:
            counter = Decimal(1)
            res = Decimal(1)
            while True:
                if counter < num:
                    res *= counter
                    counter += 1
                else:
                    break
            return res

    def fact(self):
        self.update_expr('fact')
        try:
            self.numtext = str(self.factorial(Decimal(self.numtext)))
            self.update_()
        except:
            pass

    def deg(self):
        if self.ui.btn_s_deg.text() == 'DEG':
            self.ui.btn_s_deg.setText('RAD')
        else:
            self.ui.btn_s_deg.setText('DEG')

    def hyp(self):
        if self.ui.btn_s_hyp.styleSheet() == '':
            self.ui.btn_s_hyp.setStyleSheet('color: blue;')
            self.ui.btn_s_sin.setText('sinh')
            self.ui.btn_s_cos.setText('cosh')
            self.ui.btn_s_tan.setText('tanh')
            self.ui.btn_s_asin.setText('sinh⁻¹')
            self.ui.btn_s_acos.setText('cosh⁻¹')
            self.ui.btn_s_atan.setText('tanh⁻¹')

        else:
            self.ui.btn_s_hyp.setStyleSheet('')
            self.ui.btn_s_sin.setText('sin')
            self.ui.btn_s_cos.setText('cos')
            self.ui.btn_s_tan.setText('tan')
            self.ui.btn_s_asin.setText('sin⁻¹')
            self.ui.btn_s_acos.setText('cos⁻¹')
            self.ui.btn_s_atan.setText('tan⁻¹')

    def _deg(self):
        return self.ui.btn_s_deg.text() == 'DEG'

    def _hyp(self):
        return not self.ui.btn_s_hyp.styleSheet() == ''

    def sin(self):
        num = Decimal(self.numtext)
        try:
            if self._hyp():
                self.update_expr('sinh')
                res = math.sinh(num)
            elif self._deg():
                self.update_expr('sin<d>')
                res = math.sin(num / 180 * Decimal(math.pi))
            else:
                self.update_expr('sin<r>')
                res = math.sin(num)
            res = Decimal(res).normalize()
            self.numtext = str(res)
        except Exception as E:
            print(E)

    def cos(self):
        num = Decimal(self.numtext)
        try:
            if self._hyp():
                self.update_expr('cosh')
                res = math.cosh(num)
            elif self._deg():
                self.update_expr('cos<d>')
                res = math.cos(num / 180 * Decimal(math.pi))
            else:
                self.update_expr('cos<r>')
                res = math.cos(num)
            res = Decimal(res).normalize()
            self.numtext = str(res)
        except Exception as E:
            print(E)

    def tan(self):
        num = Decimal(self.numtext)
        try:
            if self._hyp():
                self.update_expr('tanh')
                res = math.tanh(num)
            elif self._deg():
                self.update_expr('tan<d>')
                res = math.tan(num / 180 * Decimal(math.pi))
            else:
                self.update_expr('tan<r>')
                res = math.tan(num)
            res = Decimal(res).normalize()
            self.numtext = str(res)
        except Exception as E:
            print(E)

    def asin(self):
        num = Decimal(self.numtext)
        try:
            if self._hyp():
                self.update_expr('asinh')
                res = math.asinh(num)
            elif self._deg():
                self.update_expr('asin<d>')
                res = math.asin(num / 180 * Decimal(math.pi))
            else:
                self.update_expr('asin<r>')
                res = math.asin(num)
            res = Decimal(res).normalize()
            self.numtext = str(res)
        except Exception as E:
            print(E)

    def acos(self):
        num = Decimal(self.numtext)
        try:
            if self._hyp():
                self.update_expr('acosh')
                res = math.acosh(num)
            elif self._deg():
                self.update_expr('acos<d>')
                res = math.acos(num / 180 * Decimal(math.pi))
            else:
                self.update_expr('acos<r>')
                res = math.acos(num)
            res = Decimal(res).normalize()
            self.numtext = str(res)
        except Exception as E:
            print(E)

    def atan(self):
        num = Decimal(self.numtext)
        try:
            if self._hyp():
                self.update_expr('atanh')
                res = math.atanh(num)
            elif self._deg():
                self.update_expr('atan<d>')
                res = math.atan(num / 180 * Decimal(math.pi))
            else:
                self.update_expr('atan<r>')
                res = math.atan(num)
            res = Decimal(res).normalize()
            self.numtext = str(res)
        except Exception as E:
            print(E)

    def _sub(self, number: int) -> str:
        res = str(number)
        for i in range(10):
            res = res.replace(chr(i + 48), chr(0x2080 + i))
        return res

    def _update_braket(self):
        if self.brackets > 0:
            self.ui.btn_s_bra.setText('(' + self._sub(self.brackets))
        else:
            self.ui.btn_s_bra.setText('(')

    def bra(self):
        self.brackets += 1
        self._update_braket()

    def ket(self):
        self.brackets -= 1
        self._update_braket()

    def lock_keys(self):
        for btn in self.ui.btngrp_n_ops.buttons():
            btn.setEnabled(False)
        for btn in self.ui.btngrp_n_spec.buttons():
            btn.setEnabled(False)
        for btn in self.ui.btngrp_s_ops.buttons():
            btn.setEnabled(False)
        for btn in self.ui.btngrp_s_spec.buttons():
            btn.setEnabled(False)

        self.ui.btn_n_ce.setEnabled(True)
        self.ui.btn_s_ce.setEnabled(True)
        self.ui.btn_n_c.setEnabled(True)
        self.ui.btn_s_c.setEnabled(True)
        self.ui.btn_n_backspace.setEnabled(True)
        self.ui.btn_s_backspace.setEnabled(True)
        self.ui.btn_n_eql.setEnabled(True)
        self.ui.btn_s_eql.setEnabled(True)

    def unlock_keys(self):
        for btn in self.ui.btngrp_n_ops.buttons():
            btn.setEnabled(True)
        for btn in self.ui.btngrp_n_spec.buttons():
            btn.setEnabled(True)
        for btn in self.ui.btngrp_s_ops.buttons():
            btn.setEnabled(True)
        for btn in self.ui.btngrp_s_spec.buttons():
            btn.setEnabled(True)

    def errormsg(self, msg: str = '无效输入'):
        self.numtext = msg
        self.expr = ''
        self.clear_numbers = True
        self.error = True
        self.lock_keys()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    mainwin = MainWin()
    mainwin.show()

    sys.exit(app.exec_())
