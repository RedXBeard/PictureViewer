# -*- coding: utf-8 -*-

__version__ = '1.0.0'

import os
from PIL import Image
from glob import glob
from kivy.app import App
from kivy.lang import Builder
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.properties import (
    StringProperty, BooleanProperty, ObjectProperty,
    ListProperty, NumericProperty
)
from kivy.cache import Cache
from kivy.adapters.listadapter import ListAdapter
from kivy.factory import Factory
from kivy.utils import get_color_from_hex
from kivy.animation import Animation
from os.path import expanduser, normpath, join, basename, sep
from kivy.logger import Logger
from weakref import ref
from kivy.uix.filechooser import FileChooserListView
from kivy.core.text import LabelBase


FILE_EXTENSIONS = ['jpg', 'jpeg', 'png']
FILE_EXTENSIONS.extend(map(lambda x: x.upper(), FILE_EXTENSIONS))

FORWARD_KEY_CODES = [(275, 124), (100, 2), (274, 125)]
BACKWARD_KEY_CODES = [(276, 123), (97, 0), (273, 126)]

KIVY_FONTS = [
    {
        "name": "FiraSans",
        "fn_regular": "assets/fira-sans.regular.ttf"
    },
]

for font in KIVY_FONTS:
    LabelBase.register(**font)

DEFAULT_FONT = "FiraSans"


def get_dir(path):
    file_dir = os.path.dirname(path)
    return file_dir


class ImageSelectButton(ToggleButton, ToggleButtonBehavior):
    selected = {'down': 'DDDDDD',
                'normal': 'F5F5F5'}

    def change_color(self):
        self.background_color = get_color_from_hex(self.selected[self.state])

    def select(self, *args, **kwargs):
        pictureviewer = self.parent.parent.parent.parent.parent
        pictureviewer.load_files(self.parent.path)

    def deselect(self, *args, **kwargs):
        pass

    def _do_press(self):
        super(ImageSelectButton, self)._do_press()
        buttons = ToggleButtonBehavior.get_widgets('images')
        for button in buttons:
            if self != button:
                button.state = 'normal'
                button.is_select = False
            button.change_color()


class Pictures(GridLayout):
    path = StringProperty('')
    name = StringProperty('')
    rotation = NumericProperty(0)
    is_selected = BooleanProperty(False)


class PictureViewer(GridLayout):
    source = StringProperty("")
    files = ListProperty([])
    selected_index_onlist = NumericProperty(0)
    selectedimage = Pictures()

    def __init__(self, *args, **kwargs):
        self.filters = map(lambda x: "*.%s" % x, FILE_EXTENSIONS)
        self.path = ""
        if 'path' in kwargs:
            self.path = kwargs.pop('path')
        super(PictureViewer, self).__init__(*args, **kwargs)

    def change_image_source(self, *args, **kwargs):
        selection = args[0]

        self.selectedimage.path = selection
        self.selectedimage.name = selection.rsplit("/", 1)[1]
        self.selectedimage.rotation = 0

        anim = Animation(width=self.photo.width, t='linear', duration=.2)
        anim.start(self.picture.image_source)

    def load_files(self, selection):
        try:
            file_dir = get_dir(selection)
            self.files = []
            if os.path.isfile(selection):
                if self.picture.image_source.source != selection:
                    if self.picture.image_source.source and self.picture.image_name.text:
                        anim = Animation(width=0, t='linear', duration=.2)
                        anim.fbind('on_complete', self.change_image_source, selection)
                        anim.start(self.picture.image_source)
                    else:
                        self.picture.image_source.width = 0

                        self.selectedimage.path = selection
                        self.selectedimage.name = selection.rsplit("/", 1)[1]
                        self.selectedimage.rotation = 0

                        anim = Animation(width=self.photo.width, t='linear', duration=.2)
                        anim.start(self.picture.image_source)
                else:
                    self.selectedimage.path = selection
                    self.selectedimage.name = selection.rsplit("/", 1)[1]
                    self.selectedimage.rotation = 0

                    anim = Animation(width=self.photo.width, t='out_back', duration=1)
                    anim.start(self.picture.image_source)

            selected = {}
            for ext in FILE_EXTENSIONS:
                files = glob("%s/*.%s" % (file_dir, ext))
                for f in files:
                    tmp = {
                        'name': f.rsplit("/", 1)[1],
                        'path': f,
                        'is_selected': selection == f and True or False,
                        'rotation': 0
                    }
                    self.files.append(tmp)
                    if tmp['is_selected']:
                        selected = tmp
            self.selected_index_onlist = self.files.index(selected)
            display_range = (
                max(self.selected_index_onlist - 4, 0),
                min(self.selected_index_onlist + 5, len(self.files))
            )
            self.files = self.files[display_range[0]:display_range[1]]
            self.selected_index_onlist = self.files.index(selected)
            # TODO: filechooser also should be moved with keyboard interactions
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
            'rotation': item.get('rotation', 0),
            'is_selected': item.setdefault('is_selected', False)
        }

    def reload_images(self):
        for pic in self.list_view.children[0].children[0].children:
            im = pic.image_source
            im.reload()
        im = self.picture.image_source
        im.reload()

    def save_img(self, *args, **kwargs):
        rotation_dct = {
            90: Image.ROTATE_90,
            180: Image.ROTATE_180,
            270: Image.ROTATE_270,
        }
        rotation = self.norm_picture(self.photo.rotation, None, None)
        rotation = int(str(rotation).rsplit(".", 1)[0])
        image_path = self.picture.image_source.source
        if rotation > 0 and rotation in rotation_dct:
            im = Image.open(image_path)
            im = im.transpose(rotation_dct.get(rotation))
            im.save(image_path, quality = 95)
            Cache.remove("kv.loader", image_path)
        self.load_files(image_path)
        self.reload_images()

    def save_anim(self):
        if self.picture.image_source.source and self.picture.image_name.text:
            anim = Animation(width=0, t='in_back', duration=1)
            anim.bind(on_complete=self.save_img)
            anim.start(self.picture.image_source)

    def norm_picture(self, angle, anim, scatter):
        rotations = [-270, -180, -90, 0, 90, 180, 270]
        find_index = map(lambda x: abs(int(self.photo.rotation) - x), rotations)
        self.selectedimage.rotation = rotations[
            find_index.index(sorted(find_index)[0])]
        return self.photo.rotation

    def rotate(self, angle):
        if self.picture.image_source.source and self.picture.image_name.text:
            anim = Animation(
                rotation=self.selectedimage.rotation + angle,
                t='linear', duration=.2)
            anim.fbind('on_complete', self.norm_picture, angle)
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
                if next_index != self.selected_index_onlist:
                    self.load_files(self.files[next_index]['path'])
        except IndexError:
            pass

    def set_path(self, *args):
        try:
            selected = get_dir(args[1])
            if os.path.isdir(selected):
                selected_dir = selected
            else:
                selected_dir = get_dir(selected)
            self.file_chooser.path = selected_dir
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
        Window.bind(on_dropfile=pictureviewer.set_path)
        return pictureviewer

if __name__ == '__main__':
    import sys
    path = "/"
    if len(sys.argv) > 1:
        path = sys.argv[1]
    Window.size = 1200, 700
    Window.borderless = False
    Config.set('kivy', 'exit_on_escape', 0)
    Config.set('kivy', 'desktop', 1)
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    PictureViewerApp(path=path).run()
