__version__ = '1.0.0'

import os
from glob import glob
from kivy.app import App
from kivy.lang import Builder
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.properties import (
    StringProperty, BooleanProperty,
    ListProperty, NumericProperty
)
from kivy.utils import get_color_from_hex
from kivy.animation import Animation


FILE_EXTENSIONS = ['jpg', 'jpeg', 'png']
FILE_EXTENSIONS.extend(map(lambda x: x.upper(), FILE_EXTENSIONS))

FORWARD_KEY_CODES = [(275, 124), (100, 2)]
BACKWARD_KEY_CODES = [(276, 123), (97, 0)]


def get_dir(path):
    file_dir = os.path.dirname(path)
    return file_dir


class ImageSelectButton(ToggleButton, ToggleButtonBehavior):
    selected = {'down': 'D6D6D6',
                'normal': 'F5F5F5'}

    def change_color(self):
        self.background_color = get_color_from_hex(self.selected[self.state])

    def select(self, *args, **kwargs):
        picture_area = self.parent.parent.parent.parent.parent.picture
        picture_area.image_source.source = self.parent.path
        picture_area.image_name = self.parent.name
        # TODO: Photo change operation should be handled on one side.

    def deselect(self, *args, **kwargs):
        pass

    def _do_press(self):
        super(ImageSelectButton, self)._do_press()
        buttons = ToggleButtonBehavior.get_widgets('images')
        for button in buttons:
            if self != button:
                button.state = 'normal'
            button.change_color()


class Pictures(GridLayout):
    path = StringProperty('')
    name = StringProperty('')
    is_selected = BooleanProperty(False)


class Picture(GridLayout):
    path = StringProperty('')
    name = StringProperty('')


class PictureViewer(GridLayout):
    source = StringProperty("")
    files = ListProperty([])
    picture_path = StringProperty("")
    picture_name = StringProperty("")
    selected_index_onlist = NumericProperty(0)

    def __init__(self, *args, **kwargs):
        self.filters = map(lambda x: "*.%s" % x, FILE_EXTENSIONS)
        self.path = ""
        if 'path' in kwargs:
            self.path = kwargs.pop('path')
        super(PictureViewer, self).__init__(*args, **kwargs)

    def load_files(self, selection):
        try:
            file_dir = get_dir(selection)
            self.files = []
            if os.path.isfile(selection):
                self.picture_path = selection
                self.picture_name = selection.rsplit("/", 1)[1]
            selected = {}
            for ext in FILE_EXTENSIONS:
                files = glob("%s/*.%s" % (file_dir, ext))
                for f in files:
                    tmp = {
                        'name': f.rsplit("/", 1)[1],
                        'path': f,
                        'is_selected': selection == f and True or False
                    }
                    self.files.append(tmp)
                    if tmp['is_selected']:
                        selected = tmp
            self.selected_index_onlist = self.files.index(selected)
            display_range = (
                max(self.selected_index_onlist - 5, 0),
                min(self.selected_index_onlist + 5, len(self.files))
            )
            self.files = self.files[display_range[0]:display_range[1]]
            self.selected_index_onlist = self.files.index(selected)
            # TODO: filechooser also should be moved with keyboard interactions
            # TODO: in each photo changing smooth animation should triggerred
        except IndexError:
            pass

    def select_source(self, *args):
        try:
            selection = args[0][0]
            self.load_files(selection)
        except IndexError:
            pass

    def picturesListed(self, row_index, item):
        return {
            'path': item.get('path', ''),
            'name': item.get('name', ''),
            'is_selected': item.setdefault('is_selected', False)
        }

    def rotate(self, angle):
        if self.picture.image_source.source:
            anim = Animation(rotation=self.photo.rotation + angle, t='linear', duration=.5)
            anim.start(self.photo)

    def key_pressed(self, *args, **kwargs):
        try:
            if self.files:
                code = args[1:3]
                next_index = self.selected_index_onlist
                if code in FORWARD_KEY_CODES:
                    next_index = min(
                        self.selected_index_onlist + 1, len(self.files) - 1)
                elif code in BACKWARD_KEY_CODES:
                    next_index = max(self.selected_index_onlist - 1, 0)
                self.load_files(self.files[next_index]['path'])
        except IndexError:
            pass


class PictureViewerApp(App):
    def __init__(self, **kwargs):
        super(PictureViewerApp, self).__init__(**kwargs)
        self.path = ""
        if 'path' in kwargs:
            self.path = get_dir(kwargs.get('path'))
        Builder.load_file('assets/PictureViewer.kv')
        self.title = 'Picture Viewer'
        self.icon = 'assets/pictureViewer.icns'

    def build(self):
        pictureviewer = PictureViewer(path=self.path)
        Window.bind(on_key_down=pictureviewer.key_pressed)
        return pictureviewer

if __name__ == '__main__':
    Window.size = 1200, 700
    Window.borderless = False
    Config.set('kivy', 'exit_on_escape', 0)
    Config.set('kivy', 'desktop', 1)
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    PictureViewerApp().run()
