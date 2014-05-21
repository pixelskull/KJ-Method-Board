__version__='0.1.0'

import kivy
kivy.require('1.8.0')

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
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.properties import ObjectProperty, NumericProperty, ListProperty, BooleanProperty
from functools import partial
from kivy.base import EventLoop
EventLoop.ensure_window()

from kivy.logger import Logger
import math
import os

import kwad


# implementation for Menu widget
class Menu(Widget): 
    touches = []
    app = None;

    # save each touch in list for detecting two-finger-touch 
    def save_touch_down(self, instance, touch):
        touch.ud['menu_event'] = None
        if len(self.touches) >= 1:
            for t in self.touches:
                if t.distance(touch) <= 50:
                    callback = partial(self.open_menu, touch)
                    Clock.schedule_once(callback, 0.5)
                    touch.ud['menu_event'] = callback
        self.touches.append(touch)

    # delete touch when finger is lifted 
    def remove_touch_down(self, instance, touch):
        if touch in self.touches:
            if touch.ud['menu_event'] is not None:
                Clock.unschedule(touch.ud['menu_event'])
            self.touches.remove(touch)

    # method for opening the menu (create menu widget)
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
        self.parent.add_widget(menu)
        callback = partial(self.close_menu, menu)
        Clock.schedule_once(callback, 2.5)

    # method for closing menu
    def close_menu(self, widget, *args):
        self.parent.remove_widget(widget)

    # method for changeing view 
    def change_view(self, widget, *args):
        self.app.sm.current = 'sort'

    # initialisation method
    def __init__(self, **kwargs): #, parent
        super(Menu, self).__init__(**kwargs)
        self.app = KJMethodApp.get_running_app()
        self.bind(on_touch_down=self.save_touch_down)
        self.bind(on_touch_up=self.remove_touch_down)
        self.bind(on_touch_move=self.remove_touch_down)


# class for implementing circle widget in middel of first screen 
class LazySusan(Widget): 
    lazy_angle = NumericProperty(0) 
    tmp = None

    # called when finger touch is detected 
    def on_touch_down(self, touch):
        if Widget(pos=self.pos, size=self.size).collide_point(touch.pos[0], touch.pos[1]):
            y = (touch.y - self.center[1])
            x = (touch.x - self.center[0])
            calc = math.degrees(math.atan2(y, x))
            self.prev_angle = calc if calc > 0 else 360+calc
            self.tmp = self.lazy_angle

    # called when finger is moving 
    def on_touch_move(self, touch):
        if Widget(pos=self.pos, size=self.size).collide_point(touch.pos[0], touch.pos[1]) and self.tmp is not None:
            y = (touch.y - self.center[1])
            x = (touch.x - self.center[0])
            calc = math.degrees(math.atan2(y, x))
            new_angle = calc if calc > 0 else 360+calc
            self.lazy_angle = self.tmp + (new_angle-self.prev_angle)%360


# Class for label that is editable 
class EditableLabel(Label):
    edit = BooleanProperty(False)
    move = BooleanProperty(False)
    textinput = ObjectProperty(None, allownone=True)

    # called when touch is detected 
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and not self.edit:
            self.edit = True
        return super(EditableLabel, self).on_touch_down(touch)

    # called when touch is moving 
    def on_touch_move(self, touch): 
        self.textinput.focus = False 
        self.parent.parent.delete_scatter = False

    # called when label is edited 
    def on_edit(self, instance, value):
        if not value:
            if self.textinput:
                self.remove_widget(self.textinput)
            return
        if not self.textinput:
            self.textinput = t = TextInput(
                text=self.text, size_hint=(None, None),
                font_size=self.font_size, font_name=self.font_name,
                pos=self.pos, size=self.size, multiline=False, keyboard_mode='managed')
            self.bind(pos=t.setter('pos'), size=t.setter('size'))
            self.add_widget(self.textinput)
            self.textinput.bind(on_text_validate=self.on_text_validate, focus=self.on_text_focus)
        else:
            self.add_widget(self.textinput) 

    # called when text is entered 
    def on_text_validate(self, instance):
        self.text = instance.text
        self.edit = False

    # called when label has focus (touch on label)
    def on_text_focus(self, instance, focus):
        if focus is False or self.edit is False:
            self.text = instance.text
            self.edit = False
            self.textinput.hide_keyboard() 
            Singelton(Card).add_card(self.text) 
        else:
            self.textinput.show_keyboard()


# dummy implementation for saving Cards 
class Card():
    _instance = None
    cards = []

    # add a card to cards-list 
    def add_card(self, label): 
        if label not in self.cards:
            self.cards.append(label)
        print self.cards

    # removes a card to cards-list 
    def remove_card(self, label):
        if label in self.cards:  
            self.cards.remove(label)
        print self.cards

# method vor calling a single instance of a Class 
def Singelton(instanceClass): 
    if not instanceClass._instance: 
        instanceClass._instance = instanceClass()
    return instanceClass._instance


# implementation Class for the first Screen 
class KJMethod(FloatLayout):
    delete_scatter = BooleanProperty(False)

    # add a label to KJMethod Screen 
    def add_label(self, widget, *args): 
        s = Scatter(size_hint=(None,None), size=(100,50), pos=widget.pos)
        #(self.parent.width/2, self.parent.height/2))
        inpt = EditableLabel(text="hallo", size_hint=(None, None), size=(100, 50), keyboard_mode='managed')
        # inpt.bind(on_touch_up=show_keyboard())
        # KeyboardListener().setCallback(self.key_up)
        s.add_widget(inpt)
        self.add_widget(s)
        update = partial(self.update_scatter, s)
        Clock.schedule_interval(update, 1.0/60.0)

    # callback called for checking delete option 
    def update_scatter(self, s, dt):
        if (s.pos[1] < 0) or (s.top > Window.height) or (s.pos[0] < 0) or (s.right > Window.width):
            self.delete_scatter = True
            callback = partial(self.remove_widget_callback, s)
            Clock.schedule_once(callback, 3.0)

    # removes (delete) an scatter 
    def remove_widget_callback(self, widget, *args):
        if self.delete_scatter is True:
            Singelton(Card).remove_card(widget.children[0].text)
            self.remove_widget(widget)
            self.delete_scatter = False


# implementation Class for the second Screen
class KJSort(FloatLayout): 
    labelset = False

    # method for adding all cards to second screen  (at the moment only one label ist added)
    def add_labels(self, widget, **args): 
        if self.labelset is False:
            for label in Singelton(Card).cards:
                s = Scatter(size_hint=(None,None), size=(100,50))
                inpt = Label(text=label, size_hint=(None,None), size=(100,50), keyboard_mode='managed')
                s.add_widget(inpt)
                self.add_widget(s)
                self.labelset = True

    # init method
    def __init__(self, **kwargs): 
        super(KJSort, self).__init__(**kwargs)
        update = self.add_labels
        Clock.schedule_interval(update, 1.0/60.0)


# Dummy Class for the first Screen (definition in .kv file)
class KJMethodScreen(Screen):
    pass

# Dummy Class for the second Screen (definition in .kv file)
class KJSortScreen(Screen):
    pass

#basic Class, root for this Application
class KJMethodApp(App):
    sm = ObjectProperty(ScreenManager(transition=SlideTransition()))

    # default build method
    def build(self):
        self.sm.add_widget(KJMethodScreen(name="method"))
        self.sm.add_widget(KJSortScreen(name="sort"))
        return self.sm

#resolution settings
Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '800')
Config.write()
# Window.fullscreen = True

#debug stuff 
kwad.attach()
if __name__ == '__main__':
 	KJMethodApp().run()