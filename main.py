import kivy
kivy.require('1.0.7')

from kivy.app import App 

from kivy.config import Config

from kivy.core.window import Window

from kivy.clock import Clock

from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scatter import Scatter
from kivy.uix.vkeyboard import VKeyboard
from kivy.uix.textinput import TextInput

from kivy.properties import ObjectProperty, NumericProperty

import math
from functools import partial

from kivy.base import EventLoop
EventLoop.ensure_window()

class Menu(Widget): 

    # def on_touch_down(self, touch):
    #     print('touch down')
    #     self.create_clock

    # def on_touch_up(self, touch):
    #     print('touch up')
    #     self.delete_clock

    def create_clock(self, widget, touch, *args):
        callback = partial(self.open_menu, touch)
        Clock.schedule_once(callback, 1)
        touch.ud['event'] = callback
        print('clock created')

    def delete_clock(self, widget, touch, *args):
        Clock.unschedule(touch.ud['event'])
        print('clock deleted')

    def open_menu(self, touch, *args): 
        menu = BoxLayout(
            size_hint=(None, None),
            orientation='vertical',
            center=touch.pos)
        menu.add_widget(Button(text='a'))
        menu.add_widget(Button(text='b'))
        close = Button(text='close')
        close.bind(on_release=partial(self.close_menu, menu))
        menu.add_widget(close)
        self.add_widget(menu)

    def close_menu(self, widget, *args):
        self.remove_widget(widget)

    def __init__(self, **kwargs):
        super(Menu, self).__init__(**kwargs)
        Window.bind(on_touch_down=self.create_clock)
        Window.bind(on_touch_up=self.delete_clock)

class LazySusan(Widget): 
    angle = NumericProperty(0) 

    # def __init__(self, **kwargs):
    #     super(LazySusan,self).__init__(**kwargs)

    def on_touch_down(self, touch):
        y = (touch.y - self.center[1])
        x = (touch.x - self.center[0])
        calc = math.degrees(math.atan2(y, x))
        self.prev_angle = calc if calc > 0 else 360+calc
        self.tmp = self.angle

    def on_touch_move(self, touch):
        y = (touch.y - self.center[1])
        x = (touch.x - self.center[0])
        calc = math.degrees(math.atan2(y, x))
        new_angle = calc if calc > 0 else 360+calc
        self.angle = self.tmp + (new_angle-self.prev_angle)%360


class KJMethod(FloatLayout):
    print Window.center

	# def open_input(self):
	# 	s = Scatter()
	# 	inpt = TextInput(size_hint=(None, None), size=(100, 50), pos=(self.parent.width/2, self.parent.height/2))
	# 	s.add_widget(inpt)
	# 	self.add_widget(s)

	# def __init__(self, **kwargs):
	# 	super(KJMethod, self).__init__(**kwargs)

class KJMethodApp(App):
	def build(self):
		scene = KJMethod()
		return scene

Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '800')
Config.write()
Window.fullscreen = True
if __name__ == '__main__':
 	KJMethodApp().run()
