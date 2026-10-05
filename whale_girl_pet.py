# -*- coding: utf-8 -*-
"""
DeepSeek 鲸鱼娘桌宠 (改进版)

功能：
- 待机动画：呼吸起伏 + 尾巴摆动 + 自然眨眼 + 呆毛晃动
- 左键点击：鲸鱼娘向上蹦一下，眯眼笑
- 左键拖动：随意移动
- 右键菜单：打开 DeepSeek 对话 / 回角落 / 开机自启 / 退出

兼容性：
- 源码运行 (python whale_girl_pet.py)：自动用 pythonw 静默启动
- 打包成 exe 运行：自动指向 exe 自身，开机自启正常工作
"""
import sys
import os
import math
import webbrowser

from PyQt5.QtWidgets import QApplication, QWidget, QMenu
from PyQt5.QtCore import Qt, QTimer, QPoint, QPointF, QRectF
from PyQt5.QtGui import (
    QPainter, QColor, QPen, QBrush, QPainterPath,
    QRadialGradient, QLinearGradient, QIcon
)

# ================= 全局配置 =================
DEEPSEEK_URL = "https://chat.deepseek.com/"
WIN_W = 220
WIN_H = 220
APP_NAME = "DeepSeekWhaleGirl"   # 用于启动项文件命名

# ================= 调色板 =================
SKIN        = QColor(255, 236, 222)
HAIR        = QColor(96, 160, 250)
HAIR_DARK   = QColor(58, 118, 220)
HAIR_LIGHT  = QColor(165, 208, 255)
WHALE_BODY  = QColor(70, 130, 235)
WHALE_LIGHT = QColor(205, 230, 255)
EYE         = QColor(28, 48, 92)
BLUSH       = QColor(255, 155, 175, 170)
MOUTH       = QColor(205, 95, 115)


# =================================================================
#  绘制鲸鱼娘
# =================================================================
def draw_whale_girl(painter, W, H, t, mood="idle", click_phase=0.0):
    painter.setRenderHint(QPainter.Antialiasing, True)

    # ---------- 动画参数 ----------
    bob       = math.sin(t * 2.0) * 3.5                 # 上下漂浮
    breath    = 1.0 + math.sin(t * 2.0) * 0.014         # 呼吸缩放
    tail_wag  = math.sin(t * 2.8) * 22.0                # 尾巴摆动
    hair_sway = math.sin(t * 1.5) * 2.5                 # 头发飘动

    happy = (mood == "happy")
    if happy:
        bump = math.sin(min(click_phase, 1.0) * math.pi)
        bob -= bump * 24.0
        eye_open = max(0.10, 1.0 - bump * 1.15)         # 眯眼笑
    else:
        cyc = (t % 3.6) / 3.6
        if cyc < 0.05:                                  # 眨眼
            k = abs(cyc - 0.025) / 0.025
            eye_open = max(0.05, k)
        else:
            eye_open = 1.0

    # ---------- 坐标变换 ----------
    painter.save()
    painter.translate(W / 2.0, H / 2.0 + bob)
    painter.scale(W / 200.0 * breath, H / 200.0 * breath)
    painter.translate(-100, -100)
    painter.setPen(Qt.NoPen)

    # ================= 鲸鱼尾巴 =================
    painter.save()
    painter.translate(150, 126)
    painter.rotate(-38 + tail_wag)
    tail = QPainterPath()
    tail.moveTo(0, 0)
    tail.cubicTo(14, -24, 46, -30, 58, -8)
    tail.cubicTo(46, 14, 14, 18, 0, 6)
    tail.closeSubpath()
    g = QLinearGradient(0, -25, 55, 20)
    g.setColorAt(0.0, WHALE_BODY)
    g.setColorAt(1.0, HAIR_DARK)
    painter.setBrush(QBrush(g))
    painter.drawPath(tail)
    painter.setPen(QPen(WHALE_LIGHT, 2.0, Qt.SolidLine, Qt.RoundCap))
    painter.drawLine(QPointF(18, 1), QPointF(46, -12))
    painter.drawLine(QPointF(18, 3), QPointF(46, 12))
    painter.setPen(Qt.NoPen)
    painter.restore()

    # ================= 后发 =================
    painter.setBrush(HAIR_DARK)
    painter.drawEllipse(QPointF(100, 96), 60, 58)

    # ================= 身体 =================
    body = QPainterPath()
    body.moveTo(76, 126)
    body.cubicTo(68, 182, 132, 182, 124, 126)
    body.closeSubpath()
    g = QLinearGradient(0, 126, 0, 182)
    g.setColorAt(0.0, WHALE_BODY)
    g.setColorAt(1.0, HAIR_DARK)
    painter.setBrush(QBrush(g))
    painter.drawPath(body)
    painter.setBrush(QColor(228, 244, 255))            # 肚子
    painter.drawEllipse(QRectF(88, 138, 24, 34))

    # ================= 侧鳍（手） =================
    painter.setBrush(WHALE_BODY)
    painter.save()
    painter.translate(74, 146)
    painter.rotate(-22 + tail_wag * 0.35)
    painter.drawEllipse(QRectF(-20, -7, 24, 15))
    painter.restore()
    painter.save()
    painter.translate(126, 146)
    painter.rotate(22 - tail_wag * 0.35)
    painter.drawEllipse(QRectF(-4, -7, 24, 15))
    painter.restore()

    # ================= 头 =================
    painter.setBrush(SKIN)
    painter.drawEllipse(QPointF(100, 88), 48, 46)

    # ================= 鲸鱼鳍耳 =================
    painter.save()
    painter.translate(62, 72)
    painter.rotate(-28 + hair_sway)
    fin = QPainterPath()
    fin.moveTo(0, 0)
    fin.cubicTo(-14, -10, -12, -30, 6, -34)
    fin.cubicTo(0, -22, 2, -10, 8, -2)
    fin.closeSubpath()
    painter.setBrush(HAIR)
    painter.drawPath(fin)
    painter.restore()

    painter.save()
    painter.translate(138, 72)
    painter.rotate(28 - hair_sway)
    fin = QPainterPath()
    fin.moveTo(0, 0)
    fin.cubicTo(14, -10, 12, -30, -6, -34)
    fin.cubicTo(0, -22, -2, -10, -8, -2)
    fin.closeSubpath()
    painter.setBrush(HAIR)
    painter.drawPath(fin)
    painter.restore()

    # ================= 刘海 =================
    bang = QPainterPath()
    bang.moveTo(53, 94)
    bang.cubicTo(48, 46, 74, 30, 100, 30)
    bang.cubicTo(126, 30, 152, 46, 147, 94)
    bang.cubicTo(143, 74, 130, 66, 119, 74)
    bang.cubicTo(112, 58, 88, 58, 81, 74)
    bang.cubicTo(70, 66, 57, 74, 53, 94)
    bang.closeSubpath()
    g = QLinearGradient(0, 30, 0, 95)
    g.setColorAt(0.0, HAIR_LIGHT)
    g.setColorAt(1.0, HAIR)
    painter.setBrush(QBrush(g))
    painter.drawPath(bang)

    # ================= 呆毛 =================
    painter.save()
    painter.translate(100, 34)
    painter.rotate(-8 + hair_sway * 1.2)
    ahoge = QPainterPath()
    ahoge.moveTo(0, 0)
    ahoge.cubicTo(-4, -14, 6, -22, 14, -26)
    ahoge.cubicTo(8, -16, 8, -8, 6, 0)
    ahoge.closeSubpath()
    painter.setBrush(HAIR)
    painter.drawPath(ahoge)
    painter.restore()

    # ================= 腮红 =================
    for bx in (72, 128):
        rg = QRadialGradient(QPointF(bx, 104), 12)
        rg.setColorAt(0.0, BLUSH)
        rg.setColorAt(1.0, QColor(255, 155, 175, 0))
        painter.setBrush(QBrush(rg))
        painter.drawEllipse(QPointF(bx, 104), 12, 7)

    # ================= 眼睛 =================
    for ex in (82, 118):
        painter.save()
        painter.translate(ex, 92)
        painter.scale(1.0, eye_open)
        painter.setBrush(QColor(255, 255, 255))       # 眼白
        painter.drawEllipse(QPointF(0, 0), 9.5, 11)
        painter.setBrush(EYE)                         # 虹膜
        painter.drawEllipse(QPointF(0, 2), 7.2, 8.4)
        painter.setBrush(QColor(255, 255, 255))       # 高光
        painter.drawEllipse(QPointF(-2.8, -1.5), 3.2, 3.2)
        painter.drawEllipse(QPointF(2.5, 3.5), 1.6, 1.6)
        painter.restore()

    # ================= 嘴 =================
    painter.setPen(QPen(MOUTH, 2.0, Qt.SolidLine, Qt.RoundCap))
    painter.setBrush(Qt.NoBrush)
    mouth = QPainterPath()
    if happy:                                          # 笑得更大
        mouth.moveTo(93, 111)
        mouth.cubicTo(97, 119, 103, 119, 107, 111)
    else:
        mouth.moveTo(95, 111)
        mouth.cubicTo(97, 115, 103, 115, 105, 111)
    painter.drawPath(mouth)
    painter.setPen(Qt.NoPen)

    painter.restore()


# =================================================================
#  开机自启工具（兼容源码运行 + exe 打包）
# =================================================================
def _startup_dir():
    if sys.platform == "win32":
        return os.path.join(os.environ["APPDATA"],
                            r"Microsoft\Windows\Start Menu\Programs\Startup")
    if sys.platform == "darwin":
        return os.path.expanduser("~/Library/LaunchAgents")
    return os.path.expanduser("~/.config/autostart")


def _startup_file():
    if sys.platform == "win32":
        return os.path.join(_startup_dir(), f"{APP_NAME}.bat")
    if sys.platform == "darwin":
        return os.path.join(_startup_dir(), "com.deepseek.whalegirl.plist")
    return os.path.join(_startup_dir(), "deepseek-whalegirl.desktop")


def _app_command():
    """根据运行方式返回启动命令：源码运行 vs 打包成 exe"""
    if getattr(sys, 'frozen', False):
        # 已打包成 exe：直接启动 exe
        return f'"{sys.executable}"'
    else:
        # 源码运行：用 pythonw 静默启动脚本
        pyw = sys.executable.replace("python.exe", "pythonw.exe")
        if not os.path.exists(pyw):
            pyw = sys.executable
        return f'"{pyw}" "{os.path.abspath(__file__)}"'


def install_autostart():
    d = _startup_dir()
    os.makedirs(d, exist_ok=True)
    path = _startup_file()
    cmd = _app_command()

    if sys.platform == "win32":
        with open(path, "w", encoding="gbk") as f:
            f.write(f'@echo off\nstart "" {cmd}\n')

    elif sys.platform == "darwin":
        if getattr(sys, 'frozen', False):
            args = f"<string>{sys.executable}</string>"
        else:
            args = (f"<string>{sys.executable}</string>"
                    f"<string>{os.path.abspath(__file__)}</string>")
        plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>com.deepseek.whalegirl</string>
<key>ProgramArguments</key><array>{args}</array>
<key>RunAtLoad</key><true/>
</dict></plist>"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(plist)

    else:  # Linux
        desktop = f"""[Desktop Entry]
Type=Application
Name=DeepSeek Whale Girl
Exec={cmd}
X-GNOME-Autostart-enabled=true
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(desktop)

    return path


def uninstall_autostart():
    path = _startup_file()
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


# =================================================================
#  桌宠窗口
# =================================================================
class WhaleGirlPet(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(WIN_W, WIN_H)
        self.setWindowFlags(Qt.FramelessWindowHint
                            | Qt.WindowStaysOnTopHint
                            | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowTitle("DeepSeek 鲸鱼娘")

        # 窗口图标（任务栏 / 任务管理器里显示）
        self._set_window_icon()

        self.t = 0.0
        self.mood = "idle"
        self.click_phase = 0.0

        self._drag = False
        self._press_pos = QPoint()
        self._drag_offset = QPoint()

        # 主循环 ~30 FPS
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(33)

        self._move_to_corner()

    # ---------- 生成窗口图标（无素材也能有） ----------
    def _set_window_icon(self):
        try:
            from PyQt5.QtGui import QPixmap
            pix = QPixmap(64, 64)
            pix.fill(Qt.transparent)
            p = QPainter(pix)
            draw_whale_girl(p, 64, 64, t=0.5, mood="idle", click_phase=0.0)
            p.end()
            self.setWindowIcon(QIcon(pix))
        except Exception:
            pass

    # ---------- 帧循环 ----------
    def _tick(self):
        self.t += 0.033
        if self.mood == "happy":
            self.click_phase += 0.033 / 0.9
            if self.click_phase >= 1.0:
                self.mood = "idle"
                self.click_phase = 0.0
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        draw_whale_girl(p, self.width(), self.height(),
                        self.t, self.mood, self.click_phase)

    # ---------- 鼠标交互 ----------
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag = False
            self._press_pos = e.globalPos()
            self._drag_offset = e.globalPos() - self.frameGeometry().topLeft()
            e.accept()

    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.LeftButton:
            if (e.globalPos() - self._press_pos).manhattanLength() > 6:
                self._drag = True
            if self._drag:
                self.move(e.globalPos() - self._drag_offset)
            e.accept()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            if not self._drag:                       # 只点击，不拖动
                self.mood = "happy"
                self.click_phase = 0.0
            self._drag = False
            e.accept()

    # ---------- 右键菜单 ----------
    def contextMenuEvent(self, e):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1f2233;
                color: #e8ecff;
                border: 1px solid #3a4060;
                border-radius: 10px;
                padding: 6px;
                font-size: 13px;
            }
            QMenu::item { padding: 7px 26px 7px 14px; border-radius: 6px; }
            QMenu::item:selected { background-color: #4d6bfe; }
            QMenu::separator { height: 1px; background: #3a4060; margin: 4px 8px; }
        """)

        a_chat = menu.addAction("💬  和 DeepSeek 对话")
        a_home = menu.addAction("🏠  回到右下角")
        menu.addSeparator()

        autostart_on = os.path.exists(_startup_file())
        a_auto = menu.addAction("❌  取消开机自启" if autostart_on
                                else "🚀  设置开机自启")
        menu.addSeparator()
        a_quit = menu.addAction("👋  退出")

        act = menu.exec_(e.globalPos())
        if act == a_chat:
            webbrowser.open(DEEPSEEK_URL)
        elif act == a_home:
            self._move_to_corner()
        elif act == a_auto:
            if autostart_on:
                uninstall_autostart()
            else:
                install_autostart()
        elif act == a_quit:
            QApplication.quit()

    # ---------- 工具 ----------
    def _move_to_corner(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.width() - self.width() - 30,
                  screen.height() - self.height() - 30)


# =================================================================
#  入口
# =================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    pet = WhaleGirlPet()
    pet.show()
    sys.exit(app.exec_())
