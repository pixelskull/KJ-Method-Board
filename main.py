import kivy
kivy.require('1.8.0')

from kivy.app import App 
from kivy.config import Config
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
# from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scatter import Scatter
from kivy.uix.vkeyboard import VKeyboard
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty, NumericProperty, ListProperty
from functools import partial
from kivy.base import EventLoop
EventLoop.ensure_window()

from kivy.logger import Logger
import math
import os

import kwad

class Menu(Widget): 

    def create_clock(self, widget, touch, *args):
        # if self.collide_point(touch.pos[0], touch.pos[1]) is  True:
        if touch.is_double_tap:
            callback = partial(self.open_menu, touch)
            Clock.schedule_once(callback, 1)
            touch.ud['menu_event'] = callback 
        else: 
            touch.ud['menu_event'] = None          

    def delete_clock(self, widget, touch, *args):
        if touch.ud['menu_event'] is not None:
            Clock.unschedule(touch.ud['menu_event'])
        
    # def on_touch_move(self, touch): 
    #     print("move move move")
    #     Clock.unschedule(touch.ud['menu_event'])

    # def on_touch_up(self, touch): 
    #     print("up up up")
    #     Clock.unschedule(touch.ud['menu_event'])

    def open_menu(self, touch, *args): 
        menu = BoxLayout(
            size_hint=(None, None),
            orientation='vertical',
            center=touch.pos)
        menu.add_widget(Button(text='new', on_press=self.parent.add_label))
        menu.add_widget(Button(text='done', on_press=self.change_view))
        close = Button(text='close')
        close.bind(on_release=partial(self.close_menu, menu))
        menu.add_widget(close)
        self.add_widget(menu)

    def close_menu(self, widget, *args):
        self.remove_widget(widget)

    def change_view(self, widget, *args):
        pass
        # self.root.goto_screen("sort") 

    # def add_label(self, widget, *args):
    #     s = Scatter()
    #     inpt = TextInput(size_hint=(None, None), size=(100, 50), pos=(self.parent.width/2, self.parent.height/2))
    #     s.add_widget(inpt)
    #     self.add_widget(s)
    #     self.close_menu

    def __init__(self, **kwargs):
        super(Menu, self).__init__(**kwargs)
        self.root = KJMethodApp()
        Window.bind(on_touch_down=self.create_clock)
        Window.bind(on_touch_up=self.delete_clock)

class LazySusan(Widget): 
    lazy_angle = NumericProperty(0) 
    tmp = None

    def __init__(self, **kwargs):
        super(LazySusan,self).__init__(**kwargs)
        # self.canvas_position.append(Window.center[0])
        # self.canvas_position.append(Window.center[1])
        # self.label_position.append(Window.center[0])
        # self.label_position.append(Window.center[1])
        # self.show_area(color=(0.7, 0.7, 0.3), alpha=0.8, group='after')

    def on_touch_down(self, touch):
        if Widget(pos=self.pos, size=self.size).collide_point(touch.pos[0], touch.pos[1]):
            y = (touch.y - self.center[1])
            x = (touch.x - self.center[0])
            calc = math.degrees(math.atan2(y, x))
            self.prev_angle = calc if calc > 0 else 360+calc
            self.tmp = self.lazy_angle

    def on_touch_move(self, touch):
        if Widget(pos=self.pos, size=self.size).collide_point(touch.pos[0], touch.pos[1]) and self.tmp is not None:
            y = (touch.y - self.center[1])
            x = (touch.x - self.center[0])
            calc = math.degrees(math.atan2(y, x))
            new_angle = calc if calc > 0 else 360+calc
            self.lazy_angle = self.tmp + (new_angle-self.prev_angle)%360


class KJMethod(FloatLayout):
    # lazy_susan = ObjectProperty(LazySusan())
    def add_label(self, widget, *args): 
        s = Scatter(size_hint=(None,None), size=(100,50), pos=(self.parent.width/2, self.parent.height/2))
        inpt = TextInput(size_hint=(None, None), size=(100, 50), on_focus=self.request_vkeyboard)
        # KeyboardListener().setCallback(self.key_up)
        s.add_widget(inpt)
        print self
        self.parent.add_widget(s,0)

    def request_vkeyboard(self):
        keyboard = Window.request_keyboard(self._keyboard_close, self)
        print("keyboard")
        if keyboard.widget:
            print("keyboard")
            vkeyboard = self._keyboard.widget
            vkeyboard.layout = './qwertz.json'

    def _keyboard_close(self, *args):
        """ The active keyboard is being closed. """
        if self._keyboard:
            self._keyboard.unbind(on_key_down=self.key_down)
            self._keyboard.unbind(on_key_up=self.key_up)
            self._keyboard = None

    def key_up(self, keyboard, keycode, text, modifiers):
        self.label.text = self.label.text + keycode[1]

    def __init__(self, **kwargs):
        super(KJMethod, self).__init__(**kwargs)
        self._keyboard = None

	# def open_input(self):
	# 	s = Scatter()
	# 	inpt = TextInput(size_hint=(None, None), size=(100, 50), pos=(self.parent.width/2, self.parent.height/2))
	# 	s.add_widget(inpt)
	# 	self.add_widget(s)

class KJSort(FloatLayout): 
    pass

class KJMethodApp(App):
	# def build(self):
	# 	scene = KJMethod()
	# 	return scene

    def build(self):
        self.screens = {}
        self.screens["editor"] = KJMethod(app=self)
        self.screens["sort"] = KJSort(app=self)
        self.root = FloatLayout()
        self.goto_screen("editor")
        return self.root
 
    def goto_screen(self, screen_name):
        self.root.clear_widgets()
        self.root.add_widget(self.screens[screen_name])

Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '800')
Config.write()
# Window.fullscreen = True

kwad.attach()
if __name__ == '__main__':
 	KJMethodApp().run()
