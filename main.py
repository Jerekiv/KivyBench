app_name = "KivyBench"
__version__ = "1.0"
release_date = "1013"

# ----------------------------------------------------------------------------------------
# DEVELOPMENT MODE (TRUE / FALSE)
# ----------------------------------------------------------------------------------------

from kivy.utils import platform

if platform == 'android':
    dev_mode = False
else:
    dev_mode = True

# Size for desktop development
win_size = (558, 992)

from kivy.logger import Logger

if platform == 'android':
    from jnius import autoclass, cast


# ----------------------------------------------------------------------------------------
# CHECK API VERSION (TO HIDE DEVICE NAVIGATION BAR - RUN ON UI THREAD)
# ----------------------------------------------------------------------------------------
api_ver = 0

try:
    from xtras.runnable import run_on_ui_thread
    android_api_version = autoclass('android.os.Build$VERSION')
    AndroidView = autoclass('android.view.View')
    AndroidPythonActivity = autoclass('org.kivy.android.PythonActivity')

    Logger.info('UI_THREAD: Application runs on Android, API level {0}'.format(android_api_version.SDK_INT))
    api_ver = str(android_api_version.SDK_INT)

except ImportError:
    def run_on_ui_thread(func):
        def wrapper(*args):
            Logger.info('UI_THREAD: {0} called on non android platform'.format(func.__name__))
        return wrapper

class Navbar():
    def init(self):
        pass

    @run_on_ui_thread
    def hide_android_navbar(self):
        if platform == 'android':
            if android_api_version.SDK_INT >= 19:
                try:
                    from jnius import autoclass
                    AndroidView = autoclass('android.view.View')
                    AndroidPythonActivity = autoclass('org.kivy.android.PythonActivity')

                    view = AndroidPythonActivity.mActivity.getWindow().getDecorView()
                    view.setSystemUiVisibility(
                        AndroidView.SYSTEM_UI_FLAG_LAYOUT_STABLE |
                        AndroidView.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION |
                        AndroidView.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
                        AndroidView.SYSTEM_UI_FLAG_LOW_PROFILE |
                        AndroidView.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
                        AndroidView.SYSTEM_UI_FLAG_FULLSCREEN |
                        AndroidView.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                    )
                except:
                    print("Issue, cannot hide android nav bar")

n = Navbar()
n.hide_android_navbar()

# ----------------------------------------------------------------------------------------
# KIVY MODULES IMPORT CONTINUE...
# ----------------------------------------------------------------------------------------
import kivy
kivy.require('1.10.0') # Min version

from kivy.config import Config

if dev_mode == False:
    Config.set('graphics', 'fullscreen', 'auto')

Config.set('kivy', 'exit_on_escape', '0')

from kivy.app import App
from kivy.core.window import Window

from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button

from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle
from kivy.uix.textinput import TextInput
from kivy.clock import Clock, mainthread

import time
from datetime import datetime, timedelta
import random
import math
import gc


# ----------------------------------------------------------------------------------------
# PARAMETER CLASS - GLOBAL SETTINGS
# ----------------------------------------------------------------------------------------
class Params(object):
    def init(self):

        # TEST MODE: Override Window size (Development mode only)
        if dev_mode == True:
            Window.size = win_size

        self.w, self.h = Window.size
        Window.clearcolor = (0, 0, 0, 0)
        ws = float(self.w) / 720
        hs = float(self.h) / 1280
        self.s = min(ws, hs)
        self.refresh_rate = 1 / 60

p = Params()


# ----------------------------------------------------------------------------------------
# GLOBAL VARS - COLORS
# ----------------------------------------------------------------------------------------
x = 255
white = (1, 1, 1, 1)
black = (0, 0, 0, 1)
red = (255/x, 0/x, 0/x, 1)


# ----------------------------------------------------------------------------------------
# LABEL CLASSES
# ----------------------------------------------------------------------------------------

class Lbl(Label):
    def __init__(self, txt, fs, pos):
        super(Lbl, self).__init__(text=txt, font_size=fs, pos=pos)

        self.color = white

        self.size = (p.w, 120*p.s)
        self.text_size = self.size

        # align centre
        self.valign = "center"
        self.halign = "center"


class Img(Image):
    def __init__(self, *args):
        super(Img, self).__init__()

        # get source as argument [0]
        self.source = args[0]

        self.border = (0, 0, 0, 0)
        self.allow_stretch = True
        self.keep_ratio = False


class Btn(Button):
    def __init__(self, *args):
        super(Btn, self).__init__()

        self.text = args[0]

        self.pos = args[1]

        # self.border = (0, 0, 0, 0)
        self.font_size = 32*p.s
        self.size = (200*p.s, 100*p.s)


class Inp(TextInput):
    def __init__(self, txt, ht, pos, width):
        super(Inp, self).__init__(text=txt, hint_text=ht, pos=pos, width=width)

        self.input_filter = "int"
        self.input_type = 'number' # This is broken... (Alphanumeric keyboard is shown, instead of numeric)

        # set styles
        self.height = 80*p.s
        self.font_size = 40*p.s
        self.background_color = get_color_from_hex('#d3d3d3')
        self.multiline = False
        self.hint_text_color = get_color_from_hex('#e0e0e0')
        self.padding = [10*p.s, 15*p.s, 1*p.s, 1*p.s]
        self.chr_limit = 3

        # allowable characters!
        self.allowed = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]

    def insert_text(self, substring, from_undo=False):

        if len(self.text) >= self.chr_limit:
            substring = None

        elif substring not in self.allowed:
            substring = None

        return super(Inp, self).insert_text(substring, from_undo=from_undo)


class Sprite(Image):
    def __init__(self, *args):
        super(Sprite, self).__init__(allow_stretch=True)

        nr = random.randint(1, 8)
        self.source = 'img/sprites/' + str(nr) + '.png'

        rand_sz = random.randint(50, 150)
        self.size = (rand_sz*p.s, rand_sz*p.s)
        self.border = (0, 0, 0, 0)
        self.sz_inc = 1*p.s

        self.switch = 0

        rand_x = random.randint(1, int(p.w - self.width))
        rand_y = random.randint(1, int(p.h - self.height - 130*p.s))
        self.pos = (rand_x, rand_y)

        rand_v1 = random.randint(5, 10)
        rand_speed = random.choice([rand_v1, rand_v1 * -1])
        self.speed_x = rand_speed
        self.speed_y = rand_speed

    def animate(self):

        # bounce right
        if (self.x + self.width) > p.w:
            self.speed_x = self.speed_x * -1

        # bounce left
        if self.x < 0:
            self.speed_x = self.speed_x * -1

        # bounce bottom
        if self.y < 0:
            self.speed_y = self.speed_y * -1

        # bounce top
        if (self.y + self.height) > (p.h - 130*p.s):
            self.speed_y = self.speed_y * -1


        # update movement
        self.x += self.speed_x
        self.y += self.speed_y

        # update size
        if self.y < p.h - 130*p.s - self.height:
            if self.switch == 1:
                self.width += self.sz_inc
                self.height += self.sz_inc
                if self.height >= 150 * p.s:
                    self.switch = 0

            if self.switch == 0:
                self.width -= self.sz_inc
                self.height -= self.sz_inc
                if self.height <= 50 * p.s:
                    self.switch = 1


# ----------------------------------------------------------------------------------------
# GENERAL / UI CLASSES
# ----------------------------------------------------------------------------------------

class ExitOverlay(Widget):
    def __init__(self, **kwargs):
        super(ExitOverlay, self).__init__()

        self.width = 600 * p.s
        self.height = 350 * p.s
        self.x = p.w/2 - self.width/2
        self.y = p.h/2 - self.height/2

        # bg
        c = get_color_from_hex('#939393')
        self.canvas.add(Color(c[0], c[1], c[2], 1))
        self.canvas.add(Rectangle(pos=(self.x, self.y), size=(self.width, self.height)))

        # lbl
        self.lbl = Lbl('Exit the App?', 40*p.s, (0, self.y + self.height - 120*p.s))
        self.add_widget(self.lbl)

        # btns
        self.b1 = Btn('YES', (p.w/2 - 230 * p.s, self.y + 50*p.s))
        self.add_widget(self.b1)

        self.b2 = Btn('NO', (p.w/2 + 30 * p.s, self.y + 50 * p.s))
        self.add_widget(self.b2)


        def exit_yes(instance):
            # stop clock
            self.parent.parent.unschedule_clock_event()
            App.get_running_app().stop()
            Window.close()
            print("Exit successful")

        def exit_no(instance):
            self.parent.remove_widget(self)

        # button bindings
        self.b1.bind(on_press=exit_yes)
        self.b2.bind(on_press=exit_no)


class AndroidKey(Widget):
    def __init__(self, redirect):
        super(AndroidKey, self).__init__()
        self.go = redirect
        # pc keyboard bind
        self._keyboard = Window
        self._keyboard.bind(on_key_down=self._key_handler)

    def post_build_init(self, *args):
        # Map Android keys
        if platform == 'android':
            android.map_key(android.KEYCODE_BACK, 1000)
        win = self._app_window
        win.bind(on_keyboard=self._key_handler)

    def _key_handler(self, *args):
        key = args[1]
        if key in (1000, 27):

            if self.go == "exit":
                self.exit = ExitOverlay()
                self.add_widget(self.exit)

            return True


# ----------------------------------------------------------------------------------------
# NAV CLASSES
# ----------------------------------------------------------------------------------------

class Header(Widget):
    def __init__(self):
        super(Header, self).__init__()

        self.height = 120*p.s

        # bg
        c = get_color_from_hex('#939393')
        self.canvas.add(Color(c[0], c[1], c[2], 1))
        self.canvas.add(Rectangle(pos=(0, p.h - self.height), size=(p.w, self.height)))

        # lbl
        self.lbl = Lbl('Nr of widgets: ', 38*p.s, (20*p.s, p.h - 120*p.s))
        self.lbl.halign = 'left'
        self.add_widget(self.lbl)

        # inp
        # input - (Args: txt, txt_hint, pos, width)
        self.inp = Inp("", "Eg: 40", (p.w - 420*p.s, p.h - 100*p.s), 180*p.s)
        self.add_widget(self.inp)

        def on_focus(instance, value):
            if value:
                self.inp.background_color = white
                self.inp.hint_text = ''
                self.inp.cursor_color = red
                self.inp.cursor_blink = True
                self.inp.cursor_width = 3 * p.s
            else:
                # hide navbar (API 27+)
                n.hide_android_navbar()
                self.inp.background_color = get_color_from_hex('#d3d3d3')

        self.inp.bind(focus=on_focus)


        # btn
        self.btn = Btn('START', (p.w - 220 * p.s, p.h - 110 * p.s))
        self.add_widget(self.btn)


class Main(Widget):
    def __init__(self):
        super(Main, self).__init__()

        self.h = Header()
        self.add_widget(self.h)
        self.h.btn.bind(on_press=self.start_stop)

        self.clock = Clock.schedule_interval(self.update, p.refresh_rate)

        self.sprite_list = []

        # exit
        self.add_widget(AndroidKey("exit"))

    def start_stop(self, *args):

        # start animation
        if self.sprite_list == []:

            # fps vars
            self.start_time = time.time()
            self.frame_count = 0
            self.p_time = 0
            self.fps = 0

            try:
                nr = int(self.h.inp.text)
            except:
                nr = 2

            for i in range(nr):
                self.sprite_list.append(Sprite())

            for sprite in self.sprite_list:
                self.add_widget(sprite)

            self.h.inp.opacity = 0
            self.h.btn.text = 'STOP'

        # stop animation
        else:
            for sprite in self.sprite_list:
                self.remove_widget(sprite)

            self.sprite_list = []
            self.h.inp.opacity = 1
            self.h.lbl.text = 'Nr of widgets: '
            self.h.btn.text = 'START'


    def check_fps(self):
        self.frame_count += 1
        t = time.time()
        e_time = int(t - self.start_time)

        if e_time > self.p_time:
            self.fps = self.frame_count
            self.frame_count = 0

        self.p_time = e_time

        return self.fps


    def update(self, dt):
        try:
            for sprite in self.sprite_list:
                sprite.animate()
        except:
            pass

        if self.sprite_list != []:
            self.h.lbl.text = 'FPS: ' + str(self.check_fps())


    def unschedule_clock_event(self):
        self.clock.cancel()
        gc.collect()


# -------------------------------------------------------
# ROOT WIDGET - KIVY APP
# -------------------------------------------------------
class GameApp(App):

    def build(self):
        p.init()
        top = Widget()
        top.add_widget(Main())
        return top

    def on_start(self):
        Logger.info("App start!")
        # hide nav menu on android API 19+ devices
        self.android_set_hide_menu()

    def on_pause(self):
        Logger.info("App paused!")
        return True

    def on_stop(self):
        Logger.critical("Good Bye!")
        Window.close()

    def on_resume(self):
        Logger.info("App resumed!")
        # hide nav menu on android API 19+ devices
        self.android_set_hide_menu()
        p.on_resume = True


    @run_on_ui_thread
    def android_set_hide_menu(self):
        if android_api_version.SDK_INT >= 19:
            Logger.info('UI_THREAD: API >= 19. Set hide menu')
            view = AndroidPythonActivity.mActivity.getWindow().getDecorView()
            view.setSystemUiVisibility(
                AndroidView.SYSTEM_UI_FLAG_LAYOUT_STABLE |
                AndroidView.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION |
                AndroidView.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
                AndroidView.SYSTEM_UI_FLAG_LOW_PROFILE |
                AndroidView.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
                AndroidView.SYSTEM_UI_FLAG_FULLSCREEN |
                AndroidView.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
            )


if __name__ == "__main__":
    GameApp().run()

