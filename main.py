# -*- coding: utf-8 -*-
__version__ = '0.1.0'

import kivy
kivy.require('1.8.0')

import kwad
import math
import os.path
import json
import urllib2
import time
from functools import partial
from random import randint
from thread import start_new_thread
from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.base import ExceptionHandler
from kivy.clock import Clock
from kivy.graphics import *
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import *
from kivy.uix.button import Button
from kivy.uix.scatter import Scatter
from kivy.uix.vkeyboard import VKeyboard
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.properties import ObjectProperty, NumericProperty, ListProperty
from kivy.properties import BooleanProperty
from kivy.gesture import GestureStroke
from kivy.logger import Logger


# implementation for Menu widget
class Menu(Widget):
    touches = []
    app = None
    degree = NumericProperty(0)
    tmp = None

    # save each touch in list for detecting two-finger-touch
    def save_touch_down(self, instance, touch):
        if len(self.parent.touches) >= 1:
            for t in self.parent.touches:
                gesture = GestureStroke()
                if t is not touch:
                    if type(self.parent) is KJMethod:
                        if gesture.points_distance(t, touch) <= 160:
                            self.open_menu(touch, t)
                    else:
                        if gesture.points_distance(t, touch) <= 160:
                            self.open_simple_menu(touch, t)

    # delete touch when finger is lifted
    def remove_touch_down(self, instance, touch):
        if touch in self.touches:
            if touch.ud['menu_event'] is not None:
                Clock.unschedule(touch.ud['menu_event'])

    # computes the rotation degrees to center from middle of window
    def compute_degree(self, pos_x, pos_y):
        x = (pos_x - Window.center[0])
        y = (pos_y - Window.center[1])
        calc = math.degrees(math.atan2(y, x))
        self.degree = calc if calc > 0 else 360 + calc
        self.degree += 90

    # computes rotation based on a widget and returns that value
    def compute_rotation(self, widget, touch):
        if widget.collide_point(touch.x, touch.y):
            x = (touch.x - widget.center_x)
            y = (touch.y - widget.center_y)
            calc = math.degrees(math.atan2(y, x))
            new_angle = calc if calc > 0 else 360+calc
            return touch.ud['tmp'] + (new_angle-touch.ud['prev_angle']) % 360

    # helper method to compute the angle of a widget
    def compute_prev_angle(self, widget, touch):
        if widget.collide_point(touch.x, touch.y):
            x = touch.x - widget.center_x
            y = touch.y - widget.center_y
            calc = math.degrees(math.atan2(y, x))
            # if not touch.ud.has_key('tmp'):
            if 'tmp' not in touch.ud:
                touch.ud['tmp'] = widget.rotation
            return calc if calc > 0 else 360+calc

    # opens a full menu used in the KJ-Method Screen
    def open_menu(self, touch1, touch2, *args):
        circlesize = 135
        buttonsize = 50
        layout = FloatLayout(size_hint=(None, None),
                             size=(circlesize, circlesize))
        scatter = Scatter(size=layout.size,
                          center=touch2.pos,
                          do_scale=False,
                          do_translation=False)
        self.compute_degree(scatter.center_x,
                            scatter.center_y)
        scatter.rotation = self.degree
        button1 = Button(text='schliessen',
                         font_size=12,
                         pos_hint={'x': 0.05, 'y': 0.3},
                         size_hint=(None, None),
                         size=(buttonsize, buttonsize),
                         background_color=(1, 1, 1, 0),
                         on_release=partial(self.close_menu, scatter))
        layout.add_widget(button1)
        button2 = Button(text='weiter',
                         pos_hint={'x': 0.6, 'y': 0.3},
                         size_hint=(None, None),
                         size=(buttonsize, buttonsize),
                         background_color=(1, 1, 1, 0),
                         on_release=partial(self.open_popup, scatter))
        layout.add_widget(button2)
        button3 = Button(text='Text',
                         pos_hint={'x': 0.30, 'y': 0.65},
                         size_hint=(None, None),
                         size=(buttonsize, buttonsize),
                         background_color=(1, 1, 1, 0),
                         on_release=partial(self.new_label, scatter))
        layout.add_widget(button3)
        button4 = Button(text='Smart-\nphone',
                         pos_hint={'x': 0.35, 'y': 0},
                         size_hint=(None, None),
                         size=(buttonsize, buttonsize),
                         background_color=(1, 1, 1, 0),
                         on_release=partial(self.qrcode, scatter))
        layout.add_widget(button4)
        with button1.canvas.before:
            Color(1, 1, 1, 0.2)
            Ellipse(size_hint=(None, None),
                    size=(circlesize, circlesize),
                    angle_start=227,
                    angle_end=313)
        with button2.canvas.before:
            Color(1, 1, 1, 0.2)
            Ellipse(size_hint=(None, None),
                    size=(circlesize, circlesize),
                    angle_start=47,
                    angle_end=133)
        with button3.canvas.before:
            Color(1, 1, 1, 0.2)
            Ellipse(size_hint=(None, None),
                    size=(circlesize, circlesize),
                    angle_start=43,
                    angle_end=-43)
        with button4.canvas.before:
            Color(1, 1, 1, 0.2)
            Ellipse(size_hint=(None, None),
                    size=(circlesize, circlesize),
                    angle_start=137,
                    angle_end=223)
        if touch1 in self.parent.touches:
            self.parent.touches.remove(touch1)
        if touch2 in self.parent.touches:
            self.parent.touches.remove(touch2)

        scatter.add_widget(layout)
        self.add_widget(scatter)
        scatter.bind(on_touch_move=self.update_menu_rotation)
        scatter.bind(on_touch_up=self.enable_buttons)

    # Method for showing the QR-Code (Smartphone)
    def qrcode(self, widget, *args):
        callback = partial(self.close_menu, widget)
        Clock.schedule_once(callback, 0)
        blayout = BoxLayout(size_hint=(None, None),
                            size=(200, 200),
                            orientation='vertical')
        scatter = Scatter(size_hint=(None, None),
                          size=(blayout.size[0], blayout.size[1]+20),
                          do_scale=True,
                          do_translation=True,
                          pos=(widget.pos[0], widget.pos[1]))
        self.compute_degree(scatter.center_x, scatter.center_y)
        scatter.rotation = self.degree
        wimg = Image(source='qr.png')
        btnok = Button(text='ok',
                       size_hint=(None, None),
                       size=(scatter.size[0], 20),
                       on_press=partial(self.rmove2, scatter),
                       pos=(scatter.pos[0], scatter.pos[1]-20))
        blayout.add_widget(wimg)
        blayout.add_widget(btnok)
        scatter.add_widget(blayout)
        self.add_widget(scatter)

    # Method for opening the Simple-Menu used in all Screens
    def open_simple_menu(self, touch1, touch2, *args):
        circlesize = 120
        buttonsize = 50

        layout = FloatLayout(size_hint=(None, None),
                             size=(circlesize, circlesize))
        scatter = Scatter(size=layout.size,
                          center=touch2.pos,
                          do_scale=False,
                          do_translation=False)
        self.compute_degree(scatter.center_x, scatter.center_y)
        scatter.rotation = self.degree
        button1 = Button(text='schliessen',
                         font_size=12,
                         pos_hint={'x': 0.05, 'y': 0.27},
                         size_hint=(None, None),
                         size=(buttonsize, buttonsize),
                         background_color=(1, 1, 1, 0),
                         on_release=partial(self.close_menu, scatter))
        layout.add_widget(button1)
        button2 = Button(text='weiter',
                         pos_hint={'x': 0.55, 'y': 0.27},
                         size_hint=(None, None),
                         size=(buttonsize, buttonsize),
                         background_color=(1, 1, 1, 0),
                         on_release=partial(self.open_popup, scatter))
        layout.add_widget(button2)
        with button1.canvas.before:
            Color(1, 1, 1, 0.2)
            Ellipse(size_hint=(None, None),
                    size=(circlesize, circlesize),
                    angle_start=2,
                    angle_end=178)
        with button2.canvas.before:
            Color(1, 1, 1, 0.2)
            Ellipse(size_hint=(None, None),
                    size=(circlesize, circlesize),
                    angle_start=182,
                    angle_end=358)
        if touch1 in self.parent.touches:
            self.parent.touches.remove(touch1)
        if touch2 in self.parent.touches:
            self.parent.touches.remove(touch2)
        scatter.add_widget(layout)
        self.add_widget(scatter)
        scatter.bind(on_touch_move=self.update_menu_rotation)
        scatter.bind(on_touch_up=self.enable_buttons)

    # Opens Popup layout for changeing the Screen
    def open_popup(self, widget, *args):
        callback = partial(self.close_menu, widget)
        Clock.schedule_once(callback, 0)

        blayout = BoxLayout(size_hint=(None, None),
                            orientation='vertical',
                            size=(300, 300))
        with blayout.canvas.before:
            Color(1, 1, 1, 1)
            Rectangle(size_hint=(None, None),
                      size=blayout.size)
        scatter = Scatter(size_hint=(None, None),
                          size=blayout.size,
                          center=self.parent.center,
                          do_scale=True,
                          do_translation=True,
                          pos=((Window.width/2)-(blayout.size[0]/2),
                               (Window.height/2)-(blayout.size[1]/2)))
        layout2 = BoxLayout(
            orientation='horizontal',
            size_hint=(None, None),
            size=(300, 30))
        if type(self.parent) is KJSort:
            l = Label(text='[color=000000]Arbeitsergebnis exportieren?[/color]',
                      size=blayout.size,
                      markup=True)
            btnJa = Button(text='Ja', size=blayout.size, on_press=partial(self.export_json, scatter))
            btnNein = Button(text='Nein', size=blayout.size, on_press=partial(self.restart, scatter))
        else:
             l = Label(text='[color=000000]Nächstes Fenster aufrufen?[/color]', size=blayout.size, markup=True)
             btnJa = Button(text='Ja', size=blayout.size, on_press=partial(self.change_view, scatter))
             btnNein = Button(text='Nein', size=blayout.size, on_press=partial(self.rmove, scatter))
        blayout.add_widget(l)
        blayout.add_widget(layout2)
        layout2.add_widget(btnJa)
        layout2.add_widget(btnNein)
        scatter.add_widget(blayout)
        self.parent.add_widget(scatter)

    # Opens Popup for exporting the json File 
    def export_json(self, widget, *args):
        callback = partial(self.rmove, widget)
        Clock.schedule_once(callback, 0)

        filepath = os.path.join(os.path.dirname(__file__), 'Arbeitsergebnis.json')
        with open(filepath, 'w') as outfile:
             json.dump(Singleton(Card).cards, outfile);
        blayout = BoxLayout(
            size_hint=(None,None),
            orientation='vertical',
            size=(300, 300))
        with blayout.canvas.before:
            Color(1, 1, 1, 1)
            Rectangle(
                size_hint=(None,None),
                size= blayout.size
            )
        scatter = Scatter(
                        size_hint=(None,None),
                        size=blayout.size,
                        center=self.parent.center,
                        do_scale=True,
                        do_translation=True,
                        pos=((Window.width/2)-(blayout.size[0]/2), (Window.height/2)-(blayout.size[1]/2))
                    )
        layout2 = BoxLayout(
            orientation='horizontal',
            size_hint=(None, None),
            size=(300, 30))
        l = Label(text='[color=000000]Arbeitsergebnis exportiert. \nDatei ist im Programmorderner zu finden, \n'
                       'als Arbeitsergebnis.json[/color]',
                  size=blayout.size,
                  markup=True)
        btnok = Button(text='ok', size=blayout.size, on_press=partial(self.change_view, scatter))
        blayout.add_widget(l)
        blayout.add_widget(layout2)
        layout2.add_widget(btnok)
        scatter.add_widget(blayout)
        self.parent.add_widget(scatter)

    # helper method for Removing a Widget from Parent 
    def rmove(self, widget, *args):
        self.parent.remove_widget(widget)

    # helper method for Removing a Widget 
    def rmove2(self, widget, *args):
        self.remove_widget(widget)

    # updates the Rotation of a Widget 
    def update_menu_rotation(self, widget, touch, *args):
        for button in widget.children[0].children:
            button.disabled = True
        if not touch.ud.has_key('is_rotated'):
            touch.ud['is_rotated'] = True
        if widget.collide_point(touch.x, touch.y):
            if not touch.ud.has_key('prev_angle'): 
                touch.ud['prev_angle'] = self.compute_prev_angle(widget, touch)
            widget.rotation = self.compute_rotation(widget, touch)
        else: 
            for button in widget.children[0].children:
                button.disabled = False

    # Enables Buttons in Menu Widget 
    def enable_buttons(self, widget, touch, *args):
        for button in widget.children[0].children: 
            button.disabled = False

    # method for closing menu
    def close_menu(self, widget, *args):
        if widget.children[0].children[0].disabled is False:
            self.remove_widget(widget)
        else: 
            for button in widget.children[0].children:
                button.disabled = False

    # Method for Restarting the Application 
    def restart(self, *args):
        self.app.sm.switch_to(KJStartScreen(name='start'))

    # method for changeing view 
    def change_view(self, widget, *args):
        if widget.children[0].children[0].disabled is False:
            if type(self.parent) is KJMethod:
                self.app.sm.switch_to(KJSortScreen(name='sort'))
            elif type(self.parent) is Help: 
                self.app.sm.switch_to(KJProblemScreen(name='problem'))
            elif type(self.parent) is Problem: 
                if self.parent.label_right.text == "":
                    LazySusan.myproblem = self.parent.label_right.text
                else: 
                    LazySusan.myproblem = ""
                self.app.sm.switch_to(KJMethodScreen(name='method'))
            else:
                self.app.sm.switch_to(KJStartScreen(name='start'))
        else: 
            for button in widget.children[0].children: 
                button.disabled = False
            
    # Add a new Label with this Method 
    def new_label(self, widget, *args): 
        if widget.children[0].children[0].disabled is False: 
            self.parent.add_label(widget)
            self.close_menu(widget)
        else: 
            for button in widget.children[0].children: 
                button.disabled = False

    # initialisation method
    def __init__(self, **kwargs): #, parent
        super(Menu, self).__init__(**kwargs)
        self.app = KJMethodApp.get_running_app()
        self.bind(on_touch_down=self.save_touch_down)


# class for implementing circle widget in middel of first screen 
class LazySusan(Widget):
    myproblem = ''
    lazy_angle = NumericProperty(0) 
    tmp = None
    color = ListProperty([0,0,0,0])
    topic_label = ObjectProperty(Label)
    label1 = ObjectProperty(None)
    label2 = ObjectProperty(None)
    label3 = ObjectProperty(None)
    label4 = ObjectProperty(None)
    label5 = ObjectProperty(None)

    # called when finger touch is detected 
    def on_touch_down(self, touch):
        if self.collide_point(touch.pos[0], touch.pos[1]):
            x = (touch.x - self.center[0])
            y = (touch.y - self.center[1])
            calc = math.degrees(math.atan2(y, x))
            self.prev_angle = calc if calc > 0 else 360+calc
            self.tmp = self.lazy_angle

    # called when finger is moving 
    def on_touch_move(self, touch):
        if self.collide_point(touch.pos[0], touch.pos[1]) and self.tmp is not None:
            x = (touch.x - self.center[0])
            y = (touch.y - self.center[1])
            calc = math.degrees(math.atan2(y, x))
            new_angle = calc if calc > 0 else 360+calc
            self.lazy_angle = self.tmp + (new_angle-self.prev_angle)%360

    # Syncs the last Entrys in Card Instance and shows them in Lazy-Susan
    def sync_entrys_in_lazy_susan(self, widget, *args):
        self.topic_label.text = 'Problem: \n'+ self.myproblem
        data = Singleton(Card).cards['default'][-5:] 
        if len(data) >= 1:
            self.label1.text = data[0]
        if len(data) >= 2:
            self.label2.text = data[1]
        if len(data) >= 3:
            self.label3.text = data[2]
        if len(data) >= 4:
            self.label4.text = data[3]
        if len(data) >= 5:
            self.label5.text = data[4]
    
    # change Color to Green (not used)
    def change_color_green(self): 
        self.color = (0,1,0,0.2)

    # change Color to Grey (not used )
    def change_color_grey(self): 
        self.color = (1,1,1,0.2)

    # init method 
    def __init__(self, **kwargs):
        super(LazySusan, self).__init__(**kwargs) 
        update = self.sync_entrys_in_lazy_susan
        Clock.schedule_interval(update, 0.01)
        self.color = (1,1,1,0.2)


# Class for label that is editable 
class EditableLabel(Label):
    edit = BooleanProperty(False)
    move = BooleanProperty(False)
    textinput = ObjectProperty(None, allownone=True)
    old_text = None 

    # called when touch is detected 
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and not self.edit:
            self.edit = True
        return super(EditableLabel, self).on_touch_down(touch)

    # called when touch is moving 
    def on_touch_move(self, touch):
        try: 
            self.textinput.hide_keyboard()
        except AttributeError:
            pass 

    # called when label is edited 
    def on_edit(self, instance, value):
        if not value:
            if self.textinput:
                self.remove_widget(self.textinput)
            return
        if not self.textinput:
            self.old_text = self.text
            self.textinput = t = TextInput(
                text=self.text, 
                size_hint=(None, None),
                font_size=self.font_size, 
                font_name=self.font_name,
                pos=self.pos, size=self.size, 
                multiline=False, keyboard_mode='managed'
            )
            self.bind(pos=t.setter('pos'), size=t.setter('size'))
            self.add_widget(self.textinput)
            self.textinput.bind( focus=self.on_text_focus)
            validate = self.on_text_validate
            Clock.schedule_interval(validate,0.1)
        else:
            self.add_widget(self.textinput) 

    # called when text is entered 
    def on_text_validate(self, instance):
        if self.textinput.text is not "" and self.textinput.text is not "klick mich":
            self.text = self.textinput.text
        else: 
            self.text = "klick mich"

    # called when label has focus (touch on label)
    def on_text_focus(self, instance, focus):
        old_categorie_name = self.text
        if self.textinput.text == "klick mich" or \
                "KategorieTitel" in self.textinput.text or \
                self.textinput.text == "leer":
            self.textinput.text = ""
        if focus is False or self.edit is False:
            if self.textinput.text == "":
                self.textinput.text = "leer"
            else: 
                self.text = instance.text
                if type(self.parent) is BoxLayout:
                    Singleton(Card).rename_categorie(self.old_text, instance.text)
            self.edit = False
            self.textinput.hide_keyboard() 
        else:
            self.textinput.show_keyboard()

    # init Method 
    def __init__(self, **kwargs):
        super(EditableLabel, self).__init__(**kwargs)
        self.show_area(color=(1,1,1,0.2))


# dummy implementation for saving Cards 
class Card():
    _instance = None
    cards = {'default':[]}
    cards_changed = False
    file_exist = False
    file_changed = False
    new_entrys_from_file = []

    # add a card to cards-list 
    def add_card(self, label): 
        if label not in self.cards['default']:
            if label is not "" and label is not "klick mich":
                self.cards['default'].append(label)
                self.cards_changed = True

    # add a CardLabel to Categorie Boxlayout
    def add_card_to_categorie(self, label, categorie): 
        if not self.cards.has_key(categorie): 
            self.add_categorie(categorie)
        self.cards[categorie].append(label)
        self.cards_changed = True

    # add a new Categorie 
    def add_categorie(self, categorie): 
        self.cards[categorie] = [] 
        self.cards_changed = True

    # removes a card to cards-list 
    def remove_card(self, label):
        if label in self.cards['default']:
            if label is not '':  
                self.cards['default'].remove(label)
                self.cards_changed = True

    # remove a Card Label from Categorie
    def remove_card_from_categorie(self, label, categorie): 
        if self.cards.has_key(categorie): 
            self.cards[categorie].remove(label)
            if len(self.cards[categorie]) == 0: 
                self.remove_categorie(categorie)
                self.cards_changed = True 

    # removes Categorie (use when Categorie is Empty)
    def remove_categorie(self, categorie): 
        self.cards.pop(categorie, None) 
        self.cards_changed = True

    # changes the name of a Categorie 
    def rename_categorie(self, old_name, new_name):
        self.cards[new_name] = self.cards.pop(old_name, [])
        self.cards_changed = True

    # syncronising Cards with Json files 
    def sync_cards_withFiles(self, widget, *args):
        filepath = os.path.join(os.path.dirname(__file__), 'kj-method.json')
        main_json = open(filepath, 'r+')
        if self.cards_changed is True:
            main_data = None
            try:
                main_data = json.load(main_json)
            except Exception, e:
                pass
            with open(filepath, 'w') as outfile: 
                json.dump(self.cards, outfile)
            self.cards_changed = False 
        try:
            main_data = json.load(main_json)
            for item in main_data['default']:
                if item not in self.cards['default']:
                    self.add_card(item)
        except Exception, e:
            pass

    # Request JSON File on Server 
    def get_update_from_server(self, server): 
        while True:
            server_data = json.load(urllib2.urlopen(server))
            for entry in server_data['default']:
                self.add_card(entry)
            time.sleep(0.1)
            
    # init method 
    def __init__(self, **kwargs): 
        update = self.sync_cards_withFiles
        Clock.schedule_interval(update, 1.0)
        start_new_thread(self.get_update_from_server, ("http://perasmus.serpens.uberspace.de/dev/pascal/data.json",))

# method vor calling a single instance of a Class 
def Singleton(instanceClass): 
    if not instanceClass._instance: 
        instanceClass._instance = instanceClass()
    return instanceClass._instance

# Basic Card_Label Class 
class Card_Label(Label): 
    addable  = BooleanProperty(True)
    double = BooleanProperty(False)

    # called when touch is detected 
    def on_touch_down(self, touch): 
        if touch.is_double_tap and self.collide_point(touch.x, touch.y): 
            self.double = True 
            if type(self.parent) is BoxLayout and self.double: 
                self.parent.parent.remove_card_from_stack(self)

    # called when touch is moving 
    def on_touch_move(self, touch): 
        self.addable = True

# Class for Stacks in Second Screen
class Card_Stack(Widget):
    entry_counter = NumericProperty(0)

    # creates a new Card_Stack 
    def create_stack(self, cardlist, title_label):
        editlabel = EditableLabel(
                        text='KategorieTitel', 
                        size_hint=(None,None),
                        size=(200, 100),
                        keyboard_mode='managed'
                    )
        stack = BoxLayout(
                    size_hint=(None,None),
                    size=(200, 100*(len(cardlist)+1)),
                    orientation='vertical'
                )
        stack.add_widget(title_label)
        for card in cardlist: stack.add_widget(card) 

        with stack.canvas.before: 
            Color(1,1,1,.2)
            Rectangle(size=stack.size)

        self.add_widget(stack)

    #removes a Card object from a stack object
    def remove_card_from_stack(self, card):
        card_list = []
        title_label = None 
        for child in self.children[0].children: 
            if type(child) is EditableLabel: 
                title_label = child
            elif child.text != card.text: 
                card_list.append(child)
                child.double = False 
        scatter_pos = self.parent.pos
        if len(card_list) <= 1 and card.double: 
            self.children[0].clear_widgets()
            inpt = Card_Label(text=card.text, 
                                size_hint=(None,None),
                                size=(200,100), 
                                keyboard_mode='managed',
                                text_size=(150,None),
                                max_lines=3,
                                line_height=0.5)
            inpt2 = Card_Label(text=card_list[0].text, 
                                size_hint=(None,None),
                                size=(200,100), 
                                keyboard_mode='managed',
                                text_size=(150,None),
                                max_lines=3,
                                line_height=0.5)
            scatter = Scatter(right=scatter_pos[0], center_y=scatter_pos[1], size_hint=(None,None), size=(200, 100))
            scatter2 = Scatter(x=scatter_pos[0]+100, center_y=scatter_pos[1], size_hint=(None,None), size=(200, 100))
            scatter.add_widget(inpt)
            scatter2.add_widget(inpt2)
            inpt.addable = False
            inpt2.addable = False
            with inpt.canvas: 
                Color(1,1,1,0.2)
                Rectangle(size=inpt.size)
            with inpt2.canvas: 
                Color(1,1,1,0.2)
                Rectangle(size=inpt2.size)
            self.parent.parent.add_widget(scatter)
            self.parent.parent.add_widget(scatter2)
            self.parent.parent.remove_widget(self.parent)
            for entry in Singleton(Card).cards.pop(title_label.text, []):
                Singleton(Card).cards['default'].append(entry)
                Singleton(Card).cards_changed = True
            card.double = False
        else:
            self.children[0].clear_widgets()
            self.remove_widget(self.children[0])
            stack = BoxLayout(
                        size_hint=(None,None),
                        size=(200, 100*(len(card_list)+1)),
                        orientation='vertical'
                    )
            stack.add_widget(title_label)
            for child in card_list: stack.add_widget(child) 
            with stack.canvas.before: 
                Color(1,1,1,.2)
                Rectangle(size=stack.size)
            self.add_widget(stack)
            inpt = Card_Label(text=card.text, 
                                size_hint=(None,None),
                                size=(200,100), 
                                keyboard_mode='managed',
                                text_size=(150,None),
                                max_lines=3,
                                line_height=0.5)
            scatter = Scatter(right=scatter_pos[0], center_y=scatter_pos[1], size_hint=(None,None), size=(150, 50))
            scatter.add_widget(inpt)
            inpt.addable = False
            with inpt.canvas: 
                Color(1,1,1,0.2)
                Rectangle(size=inpt.size)
            self.parent.parent.add_widget(scatter)
            Singleton(Card).cards[title_label.text].remove(card.text)
            Singleton(Card).cards["default"].append(card.text)
            Singleton(Card).cards_changed = True
            card.double = False 


# Dummy Screen for Start Screen 
class KJStartScreen(Screen):
    pass
# Dummy App and ScreenManager Class for Start Screen 
class KJStartApp(App, ScreenManager):
    sm = ObjectProperty(ScreenManager(transition=SlideTransition()))
    # default build method
    def build(self):
        self.sm.add_widget(KJStartScreen(name='start'))
        return self.sm
# Start Widget 
class Start(Widget):
    app = None

    # Method for building the GUI 
    def gui(self, arguments):
        boxlayout_start = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            size=(300, 300),
            pos=(Window.center[0]-150,Window.center[1]-150)
            )
        s = Scatter(
            size_hint=(None, None),
            pos=self.pos,
            do_translation= False,
            do_rotation= False,
            do_scale= False
            )
        with s.canvas:
            Rectangle(
                size=boxlayout_start.size,
                source='logo.png'
            )
        boxlayout_start.add_widget(s)
        boxlayout_button = BoxLayout(
            orientation='horizontal',
            size_hint=(None, None),
            size = (boxlayout_start.size[0], 50),
            )
        button_start=Button(
            text='Start',
            font_size=20,
            background_color=(1, 1, 1, .2),
            on_press=self.change_view
            )
        button_bedienung=Button(
            text='Tutorial',
            font_size=20,
            background_color=(1, 1, 1, .2),
            on_press=self.change_view2
            )
        boxlayout_button.add_widget(button_start)
        boxlayout_button.add_widget(button_bedienung)
        boxlayout_start.add_widget(boxlayout_button)
        self.parent.add_widget(boxlayout_start)

    # change to Problem Screen
    def change_view(self, widget, **args):
        self.app.sm.switch_to(KJProblemScreen(name='problem'))

    # change to Help Screen 
    def change_view2(self, widget, **args):
        self.app.sm.switch_to(KJHelpScreen(name='help'))

    # init Method 
    def __init__(self, **kwargs):
        super(Start, self).__init__(**kwargs)
        self.app = KJStartApp.get_running_app()
        Clock.schedule_once(self.gui, 0)

# Dummy Problem Screen Class 
class KJProblemScreen(Screen):
    pass
# Problem Screen App and ScreenManager implementation 
class KJProblemApp(App, ScreenManager):
    sm = ObjectProperty(ScreenManager(transition=SlideTransition()))

    # default build method
    def build(self):
        self.sm.add_widget(KJProblemScreen(name='problem'))
        return self.sm
# Problem Widget 
class Problem(Widget):
    touches = []
    _instance = None
    app = None
    tmp = None
    degree = NumericProperty(0)
    label_right = ObjectProperty(Label)

    # saves the touch object in touches Array
    def save_touch_down(self, instance, touch):
        self.touches.append(touch)

    # delete touch when finger is lifted 
    def remove_touch_down(self, instance, touch):
        if touch in self.touches:
            self.touches.remove(touch)

    # init Mehtod 
    def __init__(self, **kwargs):
        super(Problem, self).__init__(**kwargs)
        self.app = KJProblemApp.get_running_app()
        Clock.schedule_once(self.gui, 0)
        self.bind(on_touch_down=self.save_touch_down)
        self.bind(on_touch_up=self.remove_touch_down)

    # Method for building the GUI 
    def gui(self, arguments):
        boxlayout_input = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            size=(600, 100)
            )
        my_problem = TextInput(
            size=(600, 50),
            hint_text='Thematik',
            font_size=30)
        boxlayout_input.add_widget(my_problem)
        boxlayout_input_button = BoxLayout(
            orientation='horizontal',
            size_hint=(None, None),
            size=my_problem.size
            )
        button_weiter=Button(
            text='weiter',
            font_size=30,
            background_color=(1, 1, 1, .2)
            )
        boxlayout_input_button.add_widget(button_weiter)
        boxlayout_input.add_widget(boxlayout_input_button)
        scatter_textinput = Scatter(
            size_hint=(None, None),
            size=(my_problem.size[0], button_weiter.size[1]),
            pos= (Window.center[0]-(my_problem.size[0]/2), Window.center[1]-(my_problem.size[1]/2)),
            do_rotation=True,
            do_translation=True
            )
        scatter_textinput.add_widget(boxlayout_input)
        self.add_widget(scatter_textinput)
        label_top=Label(
            text=my_problem.text,
            font_size=30
            )
        my_problem.bind(text=label_top.setter('text'))
        scatter_labeltop=Scatter(
            size_hint=(None,None),
            size=label_top.size,
            do_rotation=False,
            do_translation=False,
            pos=(Window.center[0]-(label_top.size[0]/2), Window.height-label_top.size[1]),
            rotation=180.0
            )
        scatter_labeltop.add_widget(label_top)
        label_bottom=Label(
            text=my_problem.text,
            font_size=30
            )
        my_problem.bind(text=label_bottom.setter('text'))
        scatter_labelbottom=Scatter(
            size_hint=(None,None),
            size=label_bottom.size,
            do_rotation=False,
            do_translation=False,
            pos=(Window.center[0]-(label_bottom.size[0]/2), 0)
            )
        scatter_labelbottom.add_widget(label_bottom)
        label_left=Label(
            text=my_problem.text,
            font_size=30
            )
        my_problem.bind(text=label_left.setter('text'))
        scatter_labelleft=Scatter(
            size_hint=(None,None),
            size=label_left.size,
            do_rotation=False,
            do_translation=True,
            pos=(0, Window.center[1]-(label_left.size[0]/4)),
            rotation=630.0
            )
        scatter_labelleft.add_widget(label_left)
        label_right=Label(
            text=my_problem.text,
            font_size=30
            )
        my_problem.bind(text=label_right.setter('text'))
        scatter_labelright=Scatter(
            size_hint=(None,None),
            size=label_right.size,
            do_rotation=False,
            do_translation=False,
            pos=(Window.width-label_right.height, Window.center[1]-(label_right.width/2)),
            rotation=90.0
            )
        scatter_labelright.add_widget(label_right)
        self.parent.add_widget(scatter_labeltop)
        self.parent.add_widget(scatter_labelbottom)
        self.parent.add_widget(scatter_labelleft)
        self.parent.add_widget(scatter_labelright)
        button_weiter.bind(on_press=partial(self.change_view, label_right))

    # change Screen to Method Screen 
    def change_view(self, widget, text, **args):
        LazySusan.myproblem=widget.text
        self.app.sm.switch_to(KJMethodScreen(name='method'))

# Dummy HelpScreen 
class KJHelpScreen(Screen):
    pass
# Help Widget 
class Help(Widget):
    app=None
    touches = []

    # saves touch object in touches array 
    def save_touch_down(self, instance, touch):
        self.touches.append(touch)

    # delete touch when finger is lifted 
    def remove_touch_down(self, instance, touch):
        if touch in self.touches:
            self.touches.remove(touch)

    # Method for building the GUI 
    def gui(self, arguments):
        s1 = Scatter(
            size_hint=(None, None),
            size=(400, 300),
            pos=(Window.center[0]-420, Window.center[1])
            )
        with s1.canvas:
            Rectangle(
                size=s1.size,
                source='s1.png'
            )
        self.add_widget(s1)
        s2 = Scatter(
            size_hint=(None, None),
            size=(400, 300),
            pos=(Window.center[0]+20, Window.center[1])
            )
        with s2.canvas:
            Rectangle(
                size=s2.size,
                source='s2.png'
            )
        self.add_widget(s2)
        s3 = Scatter(
            size_hint=(None, None),
            size=(400, 300),
            pos=(Window.center[0]-420, Window.center[1]-320)
            )
        with s3.canvas:
            Rectangle(
                size=s3.size,
                source='s3.png'
            )
        self.add_widget(s3)
        s4 = Scatter(
            size_hint=(None, None),
            size=(400, 300),
            pos=(Window.center[0]+20, Window.center[1]-320)
            )
        with s4.canvas:
            Rectangle(
                size=s4.size,
                source='s4.png'
            )
        self.add_widget(s4)

    # changes Screen to Problem Screen 
    def change_view(self, **args):
        self.app.sm.switch_to(KJProblemScreen(name='problem'))

    # init Method 
    def __init__(self, **kwargs):
        super(Help, self).__init__(**kwargs)
        self.app = KJHelpScreenApp.get_running_app()
        Clock.schedule_once(self.gui, 0)
        self.bind(on_touch_down=self.save_touch_down)
        self.bind(on_touch_up=self.remove_touch_down)


# HelpScreen App and ScreenManager implementation 
class KJHelpScreenApp(App, ScreenManager):
    sm = ObjectProperty(ScreenManager(transition=SlideTransition()))

    # default build method
    def build(self):
        self.sm.add_widget(KJHelpScreen(name='help'))
        return self.sm


# implementation Class for the first Screen 
class KJMethod(FloatLayout):
    delete_scatter = BooleanProperty(False)
    touches = []
    collide = ObjectProperty(Widget)
    delete_callback = None

    # saves touch object 
    def save_touch_down(self, instance, touch):
        self.touches.append(touch)

    # delete touch when finger is lifted 
    def remove_touch_down(self, instance, touch):
        if touch in self.touches:
            self.touches.remove(touch)

    # add a label to KJMethod Screen 
    def add_label(self, widget, *args): 
        degree = self.compute_rotation(widget.center_x, widget.center_y)
        s = Scatter(size_hint=(None,None), center=widget.center, rotation=degree+110, size=(200,100))
        inpt = EditableLabel(text='klick mich', size_hint=(None, None), size=(200, 100), keyboard_mode='managed')
        s.add_widget(inpt)
        self.add_widget(s)

    # called when touch event is ended 
    def on_touch_up(self, touch):
        for child in self.children: 
            if child.pos[1] < 0 or child.top > Window.height \
                    or child.pos[0] < 0 or child.right > Window.width:
                self.delete_scatter = True
                remove_callback = partial(self.remove_widget_callback, child)
                Clock.schedule_once(remove_callback, 3.)
            collide = Widget(size_hint=(None,None),
                                    size=(Window.width/10, Window.height/10),
                                    center=Window.center)
            collide.show_area()
            if type(child) is LazySusan: 
                for child2 in self.children:
                    if child2.collide_widget(collide) and \
                        type(child2) is not LazySusan  and \
                        type(child2) is not Menu: 
                        if len(child2.children) >= 1:
                            if type(child2.children[0]) is EditableLabel and \
                                child2.children[0].text != "klick mich" and \
                                child2.children[0].text != "KategorieTitel" and \
                                child2.children[0].text != "leer":
                                try: 
                                    Singleton(Card).add_card(child2.children[0].text)
                                    self.remove_widget(child2)
                                    child2.children[0].textinput.hide_keyboard()
                                except AttributeError: 
                                    pass

    # removes (delete) an scatter 
    def remove_widget_callback(self, widget, *args):
        if self.delete_scatter and type(widget.children[0]) is not FloatLayout:
            Singleton(Card).remove_card(widget.children[0].text) 
            self.remove_widget(widget)
            self.delete_scatter = False

    # computes the Rotation to Window center 
    def compute_rotation(self, pos_x, pos_y): 
        x = (pos_x - Window.center[0])
        y = (pos_y - Window.center[1])
        calc = math.degrees(math.atan2(y, x))
        return calc if calc > 0 else 360+calc

    # init Method 
    def __init__(self, **kwargs): 
        super(KJMethod, self).__init__(**kwargs)
        self.bind(on_touch_down=self.save_touch_down)
        self.bind(on_touch_up=self.remove_touch_down)
        try:
            filepath = os.path.join(os.path.dirname(__file__), 'kj-method.json')
            os.remove(filepath)
            open(filepath, 'w')
        except Exception, e:
            pass

# implementation Class for the second Screen
class KJSort(FloatLayout): 
    touches = []
    labelset = True
    _instance = None
    card_stack_counter = NumericProperty(0)

    # saves touch object in touches array 
    def save_touch_down(self, instance, touch):
        self.touches.append(touch)

    # delete touch when finger is lifted 
    def remove_touch_down(self, instance, touch):
        if touch in self.touches:
            self.touches.remove(touch)

    # method for adding all cards to second screen  (at the moment only one label ist added)
    def add_labels(self, widget, **args): 
        if not self.labelset:
            postions = []
            for label in Singleton(Card).cards['default']:
                added = False
                while not added:
                    pos_y=randint(100, self.top-100)
                    pos_x=randint(100, self.right-100)
                    degree=self.compute_rotation(pos_x, pos_y)
                    if pos_x >= self.x+100 and \
                        pos_x <= self.right-100 and \
                        pos_y >= self.y+100 and \
                        pos_y <= self.top-100:
                        if len(self.children) == 1: 
                            s = Scatter(
                                    size_hint=(None,None), 
                                    size=(200,100), 
                                    center=(pos_x, pos_y),
                                    rotation=degree+90 
                                    )
                            self.compute_rotation(pos_x, pos_y)
                            inpt = Card_Label(text=label, 
                                            size_hint=(None,None),
                                            size=(200,100), 
                                            keyboard_mode='managed',
                                            text_size=(150,None),
                                            max_lines=3,
                                            line_height=0.5
                                            )
                            with inpt.canvas: 
                                Color(1,1,1,0.2)
                                Rectangle(size=inpt.size)
                            s.add_widget(inpt)
                            self.add_widget(s)
                            added = True
                        else: 
                            for child in self.children: 
                                
                                if not child.collide_point(pos_x, pos_y) and added is False and\
                                    type(child) is not Menu:
                                    s = Scatter(
                                        size_hint=(None,None), 
                                        size=(200,100), 
                                        center=(pos_x, pos_y),
                                        rotation=degree+90 
                                        )
                                    self.compute_rotation(pos_x, pos_y)
                                    inpt = Card_Label(text=label, 
                                                size_hint=(None,None), 
                                                size=(200,100), 
                                                keyboard_mode='managed',
                                                text_size=(150,None),
                                                max_lines=3,
                                                line_height=0.5
                                                )
                                    with inpt.canvas: 
                                        Color(1,1,1,0.2)
                                        Rectangle(size=inpt.size)
                                    s.add_widget(inpt)
                                    self.add_widget(s)
                                    added = True
                    else: 
                        added = False 
            self.labelset = True

    # called when touch event is ended 
    def on_touch_up(self, touch): 
        for child in self.children:
            if type(child) is not Menu: 
                if type(child.children[0]) is Card_Label and\
                    type(child.children[0]) is not Card_Stack:
                    for child2 in self.children: 
                        if type(child2) is not Menu: 
                            if child2.collide_widget(child) and child is not child2: 
                                if type(child2.children[0]) is Card_Label and \
                                        type(child2.children[0]) is not BoxLayout:
                                    if child2.children[0].addable and child.children[0].addable:
                                        self.create_stack(child, child2)
                try:
                    if type(child.children[0]) is Card_Stack:
                        for child2 in self.children: 
                            if type(child2) is not Menu: 
                                if child2.collide_widget(child) and child is not child2: 
                                    if type(child2.children[0] is Card_Label) and \
                                        type(child2.children[0]) is not Card_Stack and \
                                            type(child2.children[0]) is not BoxLayout:
                                        if child2.children[0].addable: 
                                            self.add_to_stack(child, child2)
                except IndexError: 
                    pass

    # creates new Stack object and add to self 
    def create_stack(self, card1, card2):
        self.card_stack_counter += 1
        degree = self.compute_rotation(card1.pos[0], card1.pos[1])
        card1.children[0].canvas.remove(Rectangle(size=card1.children[0].size))
        card2.children[0].canvas.remove(Rectangle(size=card2.children[0].size))
        c1 = card1.children[0]
        c2 = card2.children[0]
        cardlist = [Card_Label(text=c1.text, size_hint=(None,None), size=c1.size, keyboard_mode='managed'),
                    Card_Label(text=c2.text, size_hint=(None,None), size=c2.size, keyboard_mode='managed')]
        card1.clear_widgets()
        card2.clear_widgets()
        self.remove_widget(card1)
        self.remove_widget(card2)
        title_label = EditableLabel(text='KategorieTitel'+str(self.card_stack_counter), 
                                    size_hint=(None,None),
                                    size=(150, 50),
                                    keyboard_mode='managed'
                                    )
        stack = Card_Stack()
        stack.create_stack(cardlist, title_label)
        scatter = Scatter(size_hint=(None,None), 
                            size=stack.children[0].size, 
                            pos=card1.pos,
                            rotation=degree+90
                            )
        scatter.add_widget(stack)
        self.add_widget(scatter)
        Singleton(Card).remove_card(c1.text)
        Singleton(Card).remove_card(c2.text)
        Singleton(Card).add_card_to_categorie(c1.text, title_label.text)
        Singleton(Card).add_card_to_categorie(c2.text, title_label.text)

    # add a new Card to the Stack object 
    def add_to_stack(self, stack, card):
        degree = self.compute_rotation(stack.x, stack.y)
        cardlist = []
        title_label = ObjectProperty(EditableLabel)
        c=card.children[0]

        cardlist.append(Card_Label(text=c.text, size_hint=(None,None), size=c.size, keyboard_mode='managed'))
        for layout_card in stack.children[0].children[0].children: 
            if type(layout_card) is EditableLabel: 
                title_label = layout_card
            else:
                cardlist.append(layout_card)
        card.clear_widgets()
        self.remove_widget(card)
        stack.children[0].children[0].clear_widgets()
        pos = stack.pos
        rotation = stack.rotation
        self.remove_widget(stack)
        new_stack = Card_Stack()
        new_stack.create_stack(cardlist, title_label)
        scatter = Scatter(size_hint=(None,None),
                            size=new_stack.children[0].size,
                            pos=pos, 
                            rotation=rotation
                            )
        scatter.add_widget(new_stack)
        self.add_widget(scatter)
        Singleton(Card).remove_card(c.text)
        Singleton(Card).add_card_to_categorie(c.text, title_label.text)

    # computes Rotation to Window center 
    def compute_rotation(self, pos_x, pos_y): 
        x = (pos_x - Window.center[0])
        y = (pos_y - Window.center[1])
        calc = math.degrees(math.atan2(y, x))
        return calc if calc > 0 else 360+calc

    # init method
    def __init__(self, **kwargs): 
        super(KJSort, self).__init__(**kwargs)
        update = self.add_labels
        Clock.schedule_interval(update, 0.5)
        self.bind(on_touch_down=self.save_touch_down)
        self.bind(on_touch_up=self.remove_touch_down)

# Dummy implementation for EndScreen 
class KJEndScreen(Screen):
    pass
# App and Screenmanager implementation for End-Screen 
class KJEndApp(App, ScreenManager):
    sm = ObjectProperty(ScreenManager(transition=SlideTransition()))

    # default build method
    def build(self):
        self.sm.add_widget(KJEndScreen(name='end'))
        return self.sm
# Widget for EndScreen 
class End(Widget):
    app = None

    # Method for Building the GUI 
    def gui(self, arguments):
        f = FloatLayout()
        blayout = BoxLayout(
            size_hint=(None,None),
            orientation='vertical',
            size=(300,150))
        with blayout.canvas.before:
            Color(1, 1, 1, .5)
            Rectangle(
                size_hint=(None,None),
                size= blayout.size
            )
        scatter = Scatter(
                        size_hint=(None,None),
                        size=blayout.size,
                        center=self.parent.center,
                        do_scale=False,
                        do_translation=False,
                        pos=((Window.width/2)-(blayout.size[0]/2), (Window.height/2)-(blayout.size[1]/2))
                    )
        l = Label(text='[color=000000]Wollen Sie das Arbeitsergebnis \nexportieren?[/color]',
                  size=blayout.size,
                  markup=True)
        layout2 = BoxLayout(
            orientation='horizontal',
            size_hint=(None, None),
            size=(300, 30))
        btnJa = Button(text='Ja', size=blayout.size)
        btnNein = Button(text='Nein', size=blayout.size)
        blayout.add_widget(l)
        blayout.add_widget(layout2)
        layout2.add_widget(btnJa)
        layout2.add_widget(btnNein)
        scatter.add_widget(blayout)
        f.add_widget(scatter)
        self.parent.add_widget(f)

    # init Method 
    def __init__(self, **kwargs):
        super(End, self).__init__(**kwargs)
        self.app = KJEndApp.get_running_app()
        Clock.schedule_once(self.gui, 0)


# Dummy Class for the first Screen (definition in .kv file)
class KJMethodScreen(Screen):
    pass
# Dummy Class for the second Screen (definition in .kv file)
class KJSortScreen(Screen):
    def on_enter(self):
        self.children[0].labelset = False
#basic Class, root for this Application
class KJMethodApp(App, ScreenManager):
    sm = ObjectProperty(ScreenManager(transition=SlideTransition()))

    # default build method
    def build(self):
        self.sm.add_widget(KJStartScreen(name='start'))
        return self.sm

#Settings Section
Config.set('graphics', 'fullscreen', 'auto')
Config.set('postproc','jitter_distance', '0.004')
Config.set('postproc', 'jitter_ignore_devices', 'mouse, mactouch')
Config.write()
kwad.attach()

# ExceptionHandler implementation 
class E(ExceptionHandler): 
    def handle_exception(self, inst):
        Logger.exception('Exception catched by ExceptionHandler')
        return ExceptionManager.PASS
ExceptionManager.add_handler(E())

# Appstarter
if __name__ == '__main__':
 	KJMethodApp().run()