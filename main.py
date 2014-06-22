# -*- coding: utf-8 -*-
__version__='0.1.0'

import kivy
kivy.require('1.8.0')

from kivy.app import App 
from kivy.config import Config
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import *
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout

# from kivy.uix.relativelayout import RelativeLayout

from kivy.uix.button import Button
from kivy.uix.scatter import Scatter
from kivy.uix.vkeyboard import VKeyboard
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.properties import ObjectProperty, NumericProperty, ListProperty, BooleanProperty
from functools import partial
# from kivy.base import EventLoop
# from kivy.base import EventLoopBase
from kivy.base import ExceptionHandler
from kivy.base import ExceptionManager

from kivy.gesture import GestureStroke
# EventLoop.ensure_window()

from kivy.logger import Logger
import math
# import os
import os.path
import json
from random import randint

import kwad


# implementation for Menu widget
class Menu(Widget): 
    touches = []
    app = None;
    degree = NumericProperty(0)
    tmp = None

    # save each touch in list for detecting two-finger-touch 
    def save_touch_down(self, instance, touch):
        if len(self.parent.touches) >= 1:
            for t in self.parent.touches:
                gesture = GestureStroke()
                if t is not touch:
                    if gesture.points_distance(t, touch) <= 160: 
                        self.open_menu(touch, t)


    # delete touch when finger is lifted 
    def remove_touch_down(self, instance, touch):
        if touch in self.touches:
            if touch.ud['menu_event'] is not None:
                Clock.unschedule(touch.ud['menu_event'])

    def compute_degree(self, pos_x, pos_y):
        x = (pos_x - Window.center[0])
        y = (pos_y - Window.center[1])
        calc = math.degrees(math.atan2(y, x))
        self.degree =  calc if calc > 0 else 360+calc
        self.degree += 90

    def compute_rotation(self, widget, touch):
        if widget.collide_point(touch.x, touch.y): 
            x = (touch.x - widget.center_x)
            y = (touch.y - widget.center_y)
            calc = math.degrees(math.atan2(y,x))
            new_angle = calc if calc > 0 else 360+calc
            return touch.ud['tmp'] + (new_angle-touch.ud['prev_angle'])%360

    def compute_prev_angle(self, widget, touch):
        if widget.collide_point(touch.x, touch.y): 
            x = touch.x - widget.center_x
            y = touch.y - widget.center_y
            calc = math.degrees(math.atan2(y,x))
            if not touch.ud.has_key('tmp'):
                touch.ud['tmp'] = widget.rotation
            return calc if calc > 0 else 360+calc

    def open_menu(self, touch1, touch2, *args):
        circlesize = 120
        buttonsize = 50

        layout = FloatLayout(size_hint=(None,None), size=(circlesize,circlesize))

        scatter = Scatter(size=layout.size, center=touch2.pos, do_scale=False, do_translation=False)
        self.compute_degree(scatter.center_x, scatter.center_y)
        scatter.rotation = self.degree

        # self.bind(on_degree=partial(self.update_menu_rotation, scatter))

        button1 = Button(text='close',
                        pos_hint={'x':0.2,'y':0.0},
                        size_hint=(None, None),
                        size=(buttonsize, buttonsize),
                        background_color=(1, 1, 1, 0), 
                        on_release=partial(self.close_menu, scatter))

        button2 = Button(text='done',
                        pos_hint={'x':0.5, 'y':0.5},
                        size_hint=(None,None), 
                        size=(buttonsize, buttonsize), 
                        background_color=(1,1,1,0),
                        on_release=partial(self.open_popup, scatter))
        layout.add_widget(button2)

        button3 = Button(text='input',
                        pos_hint={'x':0.0,'y':0.5},
                        size_hint=(None, None),
                        size=(buttonsize, buttonsize),
                        background_color=(1, 1, 1, 0),
                        on_release=partial(self.new_label, scatter)) 
        layout.add_widget(button3)

        self.add_widget(scatter)

        with button1.canvas.before: 
            Color(1,1,0,0.2)
            Ellipse(
                size_hint=(None, None),
                size=(circlesize, circlesize), 
                angle_start=240, 
                angle_end=120 
                )

        with button2.canvas.before: 
            Color(1,1,0.5,0.2)
            Ellipse(
                size_hint=(None, None),
                size=(circlesize, circlesize), 
                angle_start=0, 
                angle_end=120 
                )

        with button3.canvas.before: 
            Color(1, 1, 1, 0.2)
            Ellipse(
                size_hint=(None, None),
                size=(circlesize, circlesize),
                angle_start=240,
                angle_end=360
                )

        if touch1 in self.parent.touches: 
            self.parent.touches.remove(touch1)
        if touch2 in self.parent.touches: 
            self.parent.touches.remove(touch2)

        layout.add_widget(button1)
        scatter.add_widget(layout)

        scatter.bind(on_touch_move=self.update_menu_rotation)
        scatter.bind(on_touch_up=self.enable_buttons)

    def open_popup(self, widget, *args):
        callback = partial(self.close_menu, widget)
        Clock.schedule_once(callback, 0)

        blayout = BoxLayout(
            size_hint=(None,None),
            orientation='vertical',
            size=(300, 300))

        with blayout.canvas.before:
            Color(0, 0, 0, 0.8)
            Rectangle(
                size_hint=(None,None),
                size= blayout.size
            )


        scatter = Scatter(
                        size_hint=(None,None),
                        size=blayout.size, 
                        center=self.parent.center, 
                        do_scale=False, 
                        do_translation=False
                    )
        l = Label(text='Nächstes Fenster \naufrufen?', size=blayout.size)

        layout2 = BoxLayout(
            orientation='horizontal',
            size_hint=(None, None),
            size=(300, 30))

        btnJa = Button(text='Ja', size=blayout.size, on_press=partial(self.change_view, scatter))

        btnNein = Button(text='Nein', size=blayout.size, on_press=partial(self.rmove, scatter))

        blayout.add_widget(l)
        blayout.add_widget(layout2)
        layout2.add_widget(btnJa)
        layout2.add_widget(btnNein)

        scatter.add_widget(blayout)

        self.add_widget(scatter)

    def rmove(self, widget, *args):
        self.remove_widget(widget)

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
        # menu_scatter.rotation = self.degree%360

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

    # method for changeing view 
    def change_view(self, widget, *args):
        if widget.children[0].children[0].disabled is False:
            self.app.sm.switch_to(KJSortScreen(name='sort'))
        else: 
            for button in widget.children[0].children: 
                button.disabled = False

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
        # self.show_area()
        # self.bind(on_touch_up=self.remove_touch_down)
        # self.bind(on_touch_move=self.remove_touch_down)


# class for implementing circle widget in middel of first screen 
class LazySusan(Widget): 
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

    def sync_entrys_in_lazy_susan(self, widget, *args):
        self.topic_label.text = "Thema: Platzhalter"
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
            
    def change_color_green(self): 
        self.color = (0,1,0,0.2)

    def change_color_grey(self): 
        self.color = (1,1,1,0.2)

    # init method 
    def __init__(self, **kwargs):
        super(LazySusan, self).__init__(**kwargs) 
        update = self.sync_entrys_in_lazy_susan
        Clock.schedule_interval(update, 0.01)
        self.color = (1,1,1,0.2)
        # self.show_area()


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

    def on_touch_move(self, touch):
        try: 
            self.textinput.hide_keyboard()
        except AttributeError:
            pass 

    # called when touch is removed  
    # def on_touch_up(self, touch):
    #     if self.textinput is not None: 
    #         self.textinput.focus = False 
    #         self.parent.parent.delete_scatter = False

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
            self.textinput.bind( focus=self.on_text_focus) # on_text_validate=self.on_text_validate,
            validate = self.on_text_validate
            Clock.schedule_interval(validate,0.1)
        else:
            self.add_widget(self.textinput) 

    # called when text is entered 
    def on_text_validate(self, instance):
        if self.textinput.text is not "" and self.textinput.text is not "touch me":
            self.text = self.textinput.text
            # self.edit = False
        else: 
            self.text = "touch me"

    # called when label has focus (touch on label)
    def on_text_focus(self, instance, focus):
        old_categorie_name = self.text
        if self.textinput.text == "touch me" or \
                "KategorieTitel" in self.textinput.text or \
                self.textinput.text == "empty":
            self.textinput.text = ""
        if focus is False or self.edit is False:
            if self.textinput.text == "":
                self.textinput.text = "empty"
            else: 
                self.text = instance.text
                if type(self.parent) is BoxLayout:
                    Singleton(Card).rename_categorie(self.old_text, instance.text)
                    print Singleton(Card).cards
            self.edit = False
            self.textinput.hide_keyboard() 
        else:
            self.textinput.show_keyboard()

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
            if label is not "" and label is not "touch me":
                self.cards['default'].append(label)
                self.cards_changed = True

    def add_card_to_categorie(self, label, categorie): 
        if not self.cards.has_key(categorie): 
            self.add_categorie(categorie)
        self.cards[categorie].append(label)
        self.cards_changed = True

    def add_categorie(self, categorie): 
        self.cards[categorie] = [] 
        self.cards_changed = True

    # removes a card to cards-list 
    def remove_card(self, label):
        print "remove form cards: ", label 
        if label in self.cards['default']:
            if label is not '':  
                self.cards['default'].remove(label)
                print "removed form cards: ", label 
                self.cards_changed = True

    def remove_card_from_categorie(self, label, categorie): 
        if self.cards.has_key(categorie): 
            self.cards[categorie].remove(label)
            if len(self.cards[categorie]) == 0: 
                self.remove_categorie(categorie)
                self.cards_changed = True 

    def remove_categorie(self, categorie): 
        self.cards.pop(categorie, None) 
        self.cards_changed = True

    def rename_categorie(self, old_name, new_name):
        self.cards[new_name] = self.cards.pop(old_name, [])
        self.cards_changed = True

    # syncronising Cards with Json files 
    def sync_cards_withFiles(self, widget, *args):
        # with open('lazy.json', 'w') as outfile: 
        #     json.dump(self.cards['default'][-5:], outfile);
        if self.cards_changed is True:
            filepath = os.path.join(os.path.dirname(__file__), 'kj-method.json')
            main_json = open(filepath, 'r+')
            # main_json = open('./kj-method.json', 'r+')
            main_data = None
            try:
                main_data = json.load(main_json)
            except Exception, e:
                pass
            # with open('./kj-method.json', 'w') as outfile:
            with open(filepath, 'w') as outfile: 
                json.dump(self.cards, outfile)
            self.cards_changed = False 
        filepath = os.path.join(os.path.dirname(__file__), 'kj-method.json')
        # main_json = open('./kj-method.json', 'r+')
        main_json = open(filepath, 'r+')
        try:
            main_data = json.load(main_json)
            for item in main_data['default']:
                if item not in self.cards['default']:
                    self.add_card(item)
        except Exception, e:
            pass

    # init method 
    def __init__(self, **kwargs): 
        update = self.sync_cards_withFiles
        Clock.schedule_interval(update, 1.0)


# method vor calling a single instance of a Class 
def Singleton(instanceClass): 
    if not instanceClass._instance: 
        instanceClass._instance = instanceClass()
    return instanceClass._instance


# Class for Stacks in Second Screen
class Card_Stack(Widget):
    entry_counter = NumericProperty(0)

    def create_stack(self, cardlist, title_label):
        print "len(cardlist) -> ", len(cardlist)
        print "cardlist -> ", cardlist

        editlabel = EditableLabel(
                        text='KategorieTitel', 
                        size_hint=(None,None),
                        size=(150, 50),
                        keyboard_mode='managed'
                    )

        stack = BoxLayout(
                    size_hint=(None,None),
                    size=(150, 50*(len(cardlist)+1)),
                    orientation='vertical'#,
                    #padding=(20,20,20,20)
                )
        stack.add_widget(title_label)
        for card in cardlist: stack.add_widget(card) 

        with stack.canvas.before: 
            Color(1,1,1,.2)
            Rectangle(size=stack.size)

        self.add_widget(stack)

    def remove_card_from_stack(self, stack, card): # TODO on long touch remove the label 
        pass # stack.remove_widget(card)

    # def __init__(self, **kwargs): 
    #     super(Card_Stack, self).__init__(**kwargs)
    #     with self.canvas: 
    #             Color(1,1,1,.2)
    #             Rectangle(size=self.size)
        


# implementation Class for the first Screen 
class KJMethod(FloatLayout):
    delete_scatter = BooleanProperty(False)

    touches = []
    collide = ObjectProperty(Widget)
    delete_callback = None


    def save_touch_down(self, instance, touch):
        self.touches.append(touch)
        print 'added', touch

    # delete touch when finger is lifted 
    def remove_touch_down(self, instance, touch):
        print 'remove', touch
        if touch in self.touches:
            self.touches.remove(touch)
            # print self.touches

    # add a label to KJMethod Screen 
    def add_label(self, widget, *args): 
        degree = self.compute_rotation(widget.center_x, widget.center_y)
        # degree = widget.rotation - 90
        # scatter_pos = widget.pos

        s = Scatter(size_hint=(None,None), center=widget.center, rotation=degree+110) # , size=(100,50)
        inpt = EditableLabel(text='touch me', size_hint=(None, None), size=(100, 50), keyboard_mode='managed')
        # inpt.bind(on_touch_up=show_keyboard())
        # KeyboardListener().setCallback(self.key_up)
        s.add_widget(inpt)
        # s.show_area()
        self.add_widget(s)

    def on_touch_up(self, touch):
        print "-------> ", touch, "<----------" 
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
                    # print child2 
                    # if collide.collide_widget(child2) and \
                    if child2.collide_widget(collide) and \
                        type(child2) is not LazySusan  and \
                        type(child2) is not Menu: 
                        if len(child2.children) >= 1:
                            print child2
                            if type(child2.children[0]) is EditableLabel and \
                                child2.children[0].text != "touch me" and \
                                child2.children[0].text != "KategorieTitel" and \
                                child2.children[0].text != "empty":
                                try: 
                                    print "collide LazySusan", child, child2.children
                                    Singleton(Card).add_card(child2.children[0].text)
                                    self.remove_widget(child2)
                                    
                                    child2.children[0].textinput.hide_keyboard()
                                except AttributeError: 
                                    pass

    # removes (delete) an scatter 
    def remove_widget_callback(self, widget, *args):
        if self.delete_scatter and type(widget.children[0]) is not FloatLayout:
            print "----------->remove widget"
            Singleton(Card).remove_card(widget.children[0].text) 
            self.remove_widget(widget)
            self.delete_scatter = False

    def compute_rotation(self, pos_x, pos_y): 
        x = (pos_x - Window.center[0])
        y = (pos_y - Window.center[1])
        calc = math.degrees(math.atan2(y, x))
        return calc if calc > 0 else 360+calc

    def __init__(self, **kwargs): 
        super(KJMethod, self).__init__(**kwargs)
        self.bind(on_touch_down=self.save_touch_down)
        self.bind(on_touch_up=self.remove_touch_down)
        # self.bind(on_touch_move=self.remove_touch_down)
        try:
            filepath = os.path.join(os.path.dirname(__file__), 'kj-method.json')
            os.remove(filepath)
            open(filepath, 'w')
            # os.remove('./kj-method.json')
            # open('./kj-method.json', 'w')
        except Exception, e:
            pass

# implementation Class for the second Screen
class KJSort(FloatLayout): 
    labelset = True
    _instance = None
    card_stack_counter = NumericProperty(0)

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
                        if len(self.children) == 0: 
                            s = Scatter(
                                    size_hint=(None,None), 
                                    size=(100,50), 
                                    center=(pos_x, pos_y),
                                    rotation=degree+90 
                                )
                            print 'added label: ' + label
                            self.compute_rotation(pos_x, pos_y)
                            inpt = Label(text=label, size_hint=(None,None), size=(100,50), keyboard_mode='managed')
                            with inpt.canvas: 
                                Color(1,1,1,0.2)
                                Rectangle(size=inpt.size)
                            s.add_widget(inpt)
                            self.add_widget(s)
                            added = True
                        else: 
                            for child in self.children: 
                                if not child.collide_point(pos_x, pos_y) and added is False:
                                    s = Scatter(
                                        size_hint=(None,None), 
                                        size=(100,50), 
                                        center=(pos_x, pos_y),
                                        rotation=degree+90 
                                    )
                                    print 'added label: ' + label
                                    self.compute_rotation(pos_x, pos_y)
                                    inpt = Label(text=label, size_hint=(None,None), size=(100,50), keyboard_mode='managed')
                                    with inpt.canvas: 
                                        Color(1,1,1,0.2)
                                        Rectangle(size=inpt.size)
                                    s.add_widget(inpt)
                                    self.add_widget(s)
                                    added = True
                    else: 
                        added = False 
            self.labelset = True

    def on_touch_up(self, touch): 
        for child in self.children: 
            print child
            if type(child.children[0]) is Label and\
                type(child.children[0]) is not Card_Stack:
                for child2 in self.children: 
                    if child2.collide_widget(child) and child is not child2: 
                        if type(child2.children[0]) is Label: 
                            self.create_stack(child, child2)
            try:
                if type(child.children[0]) is Card_Stack:
                    for child2 in self.children: 
                        if child2.collide_widget(child) and child is not child2: 
                            if type(child2.children[0] is Label) and \
                                type(child2.children[0]) is not Card_Stack:
                                self.add_to_stack(child, child2)
            except IndexError: 
                pass


    def create_stack(self, card1, card2):
        self.card_stack_counter += 1
        degree = self.compute_rotation(card1.pos[0], card1.pos[1])
        card1.children[0].canvas.remove(Rectangle(size=card1.children[0].size))
        card2.children[0].canvas.remove(Rectangle(size=card2.children[0].size))
        c1 = card1.children[0]
        c2 = card2.children[0]
        cardlist = [Label(text=c1.text, size_hint=(None,None), size=c1.size, keyboard_mode='managed'),
                    Label(text=c2.text, size_hint=(None,None), size=c2.size, keyboard_mode='managed')]
        card1.clear_widgets()
        card2.clear_widgets()
        self.remove_widget(card1)
        self.remove_widget(card2)

        title_label = EditableLabel(
                            text='KategorieTitel'+str(self.card_stack_counter), 
                            size_hint=(None,None),
                            size=(150, 50),
                            keyboard_mode='managed'
                        )
        
        stack = Card_Stack()
        stack.create_stack(cardlist, title_label)
        print stack.children[0] 
        print "stack size: ", stack.size
        scatter = Scatter(
                        size_hint=(None,None), 
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

        print Singleton(Card).cards

        # scatter.show_area()

        # stack = Card_Stack()
        # stack.new_stack(
        #             Label(text=card1.children[0].text, pos=card1.pos),
        #             Label(text=card2.children[0].text, pos=card1.pos)
        #         )
        # degree = self.compute_rotation(card1.pos[0], card1.pos[1])
        # scatter = Scatter(
        #             size_hint=(None, None),
        #             # size=(stack.width+10, stack.height+10),
        #             pos=card1.pos, 
        #             rotation=degree+90
        #         )
        # scatter.add_widget(stack)
        # self.add_widget(scatter)
        # self.remove_widget(card1)
        # self.remove_widget(card2)

    def add_to_stack(self, stack, card):
        degree = self.compute_rotation(stack.x, stack.y)
        cardlist = []
        title_label = ObjectProperty(EditableLabel)

        c=card.children[0]
        cardlist.append(Label(text=c.text, size_hint=(None,None), size=c.size, keyboard_mode='managed'))
        for layout_card in stack.children[0].children[0].children: 
            print "layout_card", layout_card.text
            print len(layout_card.parent.children)
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
        print new_stack.children[0]
        print "size of new Stack: ", new_stack.size
        scatter = Scatter(
                        size_hint=(None,None),
                        size=new_stack.children[0].size,
                        pos=pos, 
                        rotation=rotation
                    )
        scatter.add_widget(new_stack)
        self.add_widget(scatter)

        Singleton(Card).remove_card(c.text)
        Singleton(Card).add_card_to_categorie(c.text, title_label.text)

        print Singleton(Card).cards
        # scatter.show_area()

        # print 'add_card_to_stack'
        # try: 
        #     new_card = Label(text=card.children[0].text, pos=stack.pos)
        #     stack.children[0].add_card_to_stack(new_card)
        #     self.remove_widget(card)
        # except AttributeError: 
        #     pass

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
        # self.show_area()
        


# Dummy Class for the first Screen (definition in .kv file)
class KJMethodScreen(Screen):
    pass

# Dummy Class for the second Screen (definition in .kv file)
class KJSortScreen(Screen):
    # pass
    def on_enter(self):
        self.children[0].labelset = False


#basic Class, root for this Application
class KJMethodApp(App, ScreenManager):
    sm = ObjectProperty(ScreenManager(transition=SlideTransition()))

    # default build method
    def build(self):
        self.sm.add_widget(KJMethodScreen(name='method'))
        # self.sm.add_widget(KJSortScreen(name='sort'))
        return self.sm

    # def build_config(self, config): 
    #     pass

#resolution settings
Config.set('graphics', 'width', '1600')
Config.set('graphics', 'height', '1200')
Config.set('postproc','jitter_distance', '0.004')
Config.set('postproc', 'jitter_ignore_devices', 'mouse, mactouch')
Config.write()
# Window.fullscreen = True

#debug stuff 
kwad.attach()

# ExceptionHandler implementation 
# class E(ExceptionHandler): 
#     def handle_exception(self, inst):
#         Logger.exception('Exception catched by ExceptionHandler')
#         return ExceptionManager.PASS
# ExceptionManager.add_handler(E())

if __name__ == '__main__':
 	KJMethodApp().run()