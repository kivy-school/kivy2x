from kivy.app import App
from kivy.lang import Builder

kv = """
Button:
    text: "Hello World"
"""


class MainApp(App):
    def build(self):
        return Builder.load_string(kv)


def main():
    app = MainApp()
    app.run()