import kivy
kivy.require('1.0.7')

from kivy.app import App 
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.scatter import Scatter
from kivy.uix.vkeyboard import VKeyboard
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty, NumericProperty

import math


class LazySusan(Widget): 
    angle = NumericProperty(0) 
    center_position = NumericProperty(0) 

    def __init__(self, **kwargs):
        super(LazySusan,self).__init__(**kwargs)
        # center_position = Window.center

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
