__version__ = '1.0.0'

import os
from kivy.app import App
from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import Scatter
from kivy.properties import StringProperty


class Picture(Scatter):
    pass


class PictureViewer(BoxLayout):
    source = StringProperty("")

    def select_source(self, *args):
        selection = args[0]
        file_dir = os.path.dirname(selection)
        


class PictureViewerApp(App):
    def __init__(self, **kwargs):
        super(PictureViewerApp, self).__init__(**kwargs)
        Builder.load_file('assets/PictureViewer.kv')
        self.title = 'Picture Viewer'
        self.icon = ''

    def build(self):
        pictureviewer = PictureViewer()
        return pictureviewer

if __name__ == '__main__':
    Window.borderless = False
    Config.set('kivy', 'desktop', 1)
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    PictureViewerApp().run()
