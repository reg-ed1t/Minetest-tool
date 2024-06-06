from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
import requests
import json
from datetime import datetime

def get_players(server_address, server_port):
    try:
        response = requests.get("https://servers.minetest.net/list")
        response.raise_for_status()
        plist = response.json()
        
        # Найти сервер по адресу и порту
        for server in plist['list']:
            if server['address'] == server_address and server['port'] == server_port:
                return server['clients_list']
        
        return None  # Если сервер не найден
    except requests.exceptions.RequestException as e:
        print(f'Error: {e}')
        return None



class TitleBar(FloatLayout):
    def __init__(self, **kwargs):
        super(TitleBar, self).__init__(**kwargs)
        with self.canvas.before:
            Color(0, 0, 1, 1)  
            self.rect = Rectangle(size=(8000, 5), pos=(0, 1380))

        self.label = Label(
            text='Minetest Tools', 
            size_hint=(None, None), 
            size=(200, 50), 
            pos=(250, 1400), 
            color=(1, 1, 1, 1),
            bold=True
        )
        self.add_widget(self.label)

class MyWidget(FloatLayout):
    def __init__(self, **kwargs):
        super(MyWidget, self).__init__(**kwargs)

        self.title_bar = TitleBar(size_hint=(1, None), height=100)
        self.add_widget(self.title_bar)

        self.button = Button(
            text='Update : OFF' ,
            size_hint=(None, None),
            size=(200, 60),
            pos=(250, 1200)
        )
        self.button.bind(on_press=self.toggle)
        self.add_widget(self.button)

        self.text_input = TextInput(
            hint_text='Server to follow',
            size_hint=(None, None),
            size=(700, 60),
            pos=(10, 50),
            multiline=False
        )
        self.text_input.bind(on_text_validate=self.on_enter)
        self.add_widget(self.text_input)
        self.entered_text = ''
        self.terminal_output = TextInput(
            readonly=True,
            size_hint=(None, None),
            size=(700, 700),
            pos=(10, 300),
            multiline=True
        )
        self.add_widget(self.terminal_output)

        self.started = False

    def toggle(self, instance):
        if self.button.text == 'Update : OFF':
            self.button.text = 'Update : ON'
            self.on_turn_on()
        else:
            self.button.text = 'Update : ON'
            self.on_turn_off()

    def on_turn_on(self):
        self.started = True
        Clock.schedule_interval(self.update_terminal, 3) 

    def on_turn_off(self):
        self.started = False
        Clock.unschedule(self.update_terminal)

    def update_terminal(self, dt):
        server_address, server_port = self.entered_text.split(':')
        server_port = int(server_port)
        players = get_players(server_address, server_port)
        if self.started:
            
            current_time = datetime.now().strftime('%H:%M:%S')
            if players:
                self.terminal_output.text = '\n' + current_time + '\n' + '\n'.join(players) + '\n'
            else:
                self.terminal_output.text += f"[{current_time}] Error fetching player list\n"
    
    def on_enter(self, instance):
        self.entered_text = instance.text
        server_address, server_port = self.entered_text.split(':')
        server_port = int(server_port)
        players = get_players(server_address, server_port)
        current_time = datetime.now().strftime('%H:%M:%S')
        if players:
            self.terminal_output.text = '\n' + current_time + '\n' + '\n'.join(players) + '\n'
        else:
            self.terminal_output.text += f"[{current_time}] Error fetching player list\n"

class MyApp(App):
    def build(self):
        return MyWidget()

if __name__ == '__main__':
    MyApp().run()