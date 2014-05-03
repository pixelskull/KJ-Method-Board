import kivy
kivy.require('1.0.7')

from kivy.app import App 
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.scatter import Scatter
from kivy.uix.vkeyboard import VKeyboard
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty


class NumericTextInput(TextInput):
    def on_focus(self, instance, value, *largs):
        win = self.get_root_window()

        if win:
            win.release_all_keyboards()
            win._keyboards = {}

            if value: #User focus; use special keyboard
                win.set_vkeyboard_class(NumericVKeyboard)
                print "NumericVKeyboard:", win._vkeyboard_cls, VKeyboard.layout_path
            else: #User defocus; switch back to standard keyboard
                win.set_vkeyboard_class(VKeyboard)
                print ":", win._vkeyboard_cls, VKeyboard.layout_path
        return TextInput.on_focus(self, instance, value, *largs)

class KJMethod(FloatLayout):
	def open_input(self):
		s = Scatter()
		inpt = TextInput(size_hint=(None, None), size=(100, 50), pos=(self.parent.width/2, self.parent.height/2))
		s.add_widget(inpt)
		self.add_widget(s)

	def __init__(self, **kwargs):
		super(KJMethod, self).__init__(**kwargs)

class KJMethodApp(App):
	def build(self):
		scene = KJMethod()
		return scene


if __name__ == '__main__':
 	KJMethodApp().run()
