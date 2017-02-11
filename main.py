# Keep coding and change the world..And do not forget anything..Not Again..
import os
import socket
import threading
from App_Backend.client import Client

import kivy
from kivy.graphics import Rectangle, Color, Triangle, RoundedRectangle
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.widget import Widget

kivy.require('1.9.1')
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex
from kivy.uix.listview import ListItemLabel, ListItemButton

from kivy.config import Config

Window.clearcolor = get_color_from_hex('#AA00FF')

client = None

Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '600')

Config.write()


class RootScreen(ScreenManager):
    def __init__(self, **kwargs):
        super(RootScreen, self).__init__(**kwargs)
        self.client = Client(window=ca)
        t = threading.Thread(target=self.client.connect)
        t.daemon = True
        t.start()
        self.screen_instance = {}
        self.prev_screens = set()

    def update(self):
        new_item = [item for item in self.screens if item not in self.prev_screens]
        if not new_item:
            return
        self.prev_screens = set(self.screens)
        for item in new_item:
            self.screen_instance[item.name] = item


class ClientList(Screen):
    def __init__(self, **kwargs):
        super(ClientList, self).__init__(**kwargs)
        self.screens = set()

    def update_screen(self, app, screen):
        if screen not in screen:
            app.root.add_screen(screen)
            self.screens.add(screen)
        else:
            app.root.remove_screen(screen)
            self.screens.remove(screen)


class ClientListItem(Button):
    font_size = 20
    color = get_color_from_hex("#E1BEE7")

    def __init__(self, **kwargs):
        kwargs['height'] = 40
        super(ClientListItem, self).__init__(**kwargs)
        if self.text not in Window.children[0].screen_names:
            screen = NewClient(name=self.text)
            sc_root = Window.children[0]
            sc_root.add_widget(screen)
            sc_root.prev_screens.add(screen)
            sc_root.screen_instance[self.text] = screen

    def on_release(self):
        Window.children[0].current = self.text


class NewClient(Screen):
    search_input = ObjectProperty()
    id_message_list = ObjectProperty()
    last_height = 0

    def __init__(self, *args, **kwargs):
        super(NewClient, self).__init__(**kwargs)

    def send_message(self):
        # global client
        if not self.search_input.text:
            return
        words_not_allowed = {"hindu", "muslim", "shit", }
        text = self.search_input.text
        for word in words_not_allowed:
            if word in text:
                text = "This text can't be shown"
                break
        msg_item = CustomMessageItem(text=(text, 0))
        self.id_message_list.add_widget(msg_item)
        self.search_input.text = ''
        children = self.id_message_list.children
        self.last_height = children[-1].height
        if self.id_message_list.height > self.id_message_list.parent.height:
            self.id_message_list.height += self.last_height
        self.ids.sc_view.scroll_to(msg_item)
        self.get_root_window().children[0].client.send_msg(self.name, text)

    def receive_message(self, message):
        msg_item = CustomMessageItem(text=(message, 1))
        self.id_message_list.add_widget(msg_item)
        children = self.id_message_list.children
        self.last_height = children[-1].height
        if self.id_message_list.height > self.id_message_list.parent.height:
            self.id_message_list.height += self.last_height
        self.ids.sc_view.scroll_to(msg_item)

    def update_height(self):
        children = self.id_message_list.children
        if self.id_message_list.height == self.id_message_list.parent.height:
            total_height = 0
            for child in children:
                total_height += child.height
            self.id_message_list.height = max(total_height, self.id_message_list.height)
        else:
            self.last_height -= children[0].height
            self.id_message_list.height -= self.last_height


class TabTextInput(TextInput):
    def __init__(self, *args, **kwargs):
        super(TabTextInput, self).__init__(*args, **kwargs)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[1] == 'enter':
            send_button = self.parent.parent.parent
            send_button.send_message()
            send_button.update_height()
        else:
            super(TabTextInput, self).keyboard_on_key_down(window, keycode, text, modifiers)


class CustomMessageItem(Label):
    def __init__(self, **kwargs):
        kwargs['text'], flag = kwargs['text']
        kwargs['text'] = kwargs['text'].strip()
        if flag == 1:
            kwargs['pos_hint'] = {'x': 0}
        else:
            kwargs['pos_hint'] = {'right': 1}

        super(CustomMessageItem, self).__init__(**kwargs)
        self.texture_update()


class ChatApp(App):
    title = socket.gethostname()
    root = None

    def build(self):
        self.root = RootScreen()
        return self.root

    def check(self):
        while self.root is None:
            continue
        while not self.root.ids.keys():
            continue
        print self.root.ids


if __name__ == '__main__':
    ca = ChatApp()
    ca.run()
