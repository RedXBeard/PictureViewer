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
FULLSCREEN_KEY_CODES = [(102, 3)]

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
        """
        Selected image on right sided panel must be recognized
        """
        self.background_color = get_color_from_hex(self.selected[self.state])

    def select(self, *args, **kwargs):
        """
        Selected image on right sided panel should be main photo
        """
        pictureviewer = self.parent.parent.parent.parent.parent
        pictureviewer.load_files(self.parent.path)

    def deselect(self, *args, **kwargs):
        pass

    def _do_press(self):
        """
        To handle button pressure on right sided panel
        """
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
        self.path = kwargs.pop('path')
        super(PictureViewer, self).__init__(*args, **kwargs)

    def change_item_colors(self, *args, **kwargs):
        print "???"
        for item in self.file_chooser._items:
            item.color_selected = get_color_from_hex('B3B3B3')

    def _browser_action(self, button, *args, **kwargs):
        """
        close and display browser panel action handled.
        """
        non_display = True
        if button.direction == "left":
            button.direction = "right"
            button.text = "[font=assets/fontawesome-webfont.ttf][/font]"
        else:
            non_display = False
            button.direction = "left"
            button.text = "[font=assets/fontawesome-webfont.ttf][/font]"

        for widget in self.file_chooser.layout.children[0].children:
            if str(widget).find("BoxLayout") != -1:
                step = 0
                for wwidget in widget.children:
                    if str(wwidget).find("Label") != -1:
                        if non_display:
                            wwidget.text = ""
                        else:
                            wwidget.text = step==0 and 'Size' or 'Name'
                            step += 1

    def browser_action(self, button, *args, **kwargs):
        """
        close and display browser panel action trigger.
        """
        if button.direction == "left":
            anim = Animation(width=0, d=.2, t='linear')
        else:
            anim = Animation(width=250, d=.2, t='linear')
        anim.fbind('on_complete', self._browser_action, button)
        anim.start(self.file_chooser)

    def _tracker_action(self, button, *args, **kwargs):
        """
        close and display tracker panel action handled
        """
        if button.direction == "left":
            button.direction = "right"
            button.text = "[font=assets/fontawesome-webfont.ttf][/font]"
        else:
            button.direction = "left"
            button.text = "[font=assets/fontawesome-webfont.ttf][/font]"

    def tracker_action(self, button, *args, **kwargs):
        """
        close and display tracker panel action trigger
        """
        if button.direction == "right":
            anim = Animation(width=0, d=.2, t='linear')
        else:
            anim = Animation(width=150, d=.2, t='linear')
        anim.fbind('on_complete', self._tracker_action, button)
        anim.start(self.list_view)

    def activate_buttons(self, *args, **kwargs):
        """
        Save and rotate buttons comes inactive must activated with selection.
        """
        self.rotate_left.text = self.rotate_left.pre_text
        self.rotate_right.text = self.rotate_right.pre_text
        save_image = self.save_but.children[0]
        save_image.source = "assets/save_icon.png"

    def change_image_source(self, *args, **kwargs):
        """
        Selected image action main handler.
        """
        selection = args[0]

        self.selectedimage.path = selection
        self.selectedimage.name = selection.rsplit("/", 1)[1]
        self.selectedimage.rotation = 0
        self.activate_buttons()
        anim = Animation(width=self.photo.width, t='linear', duration=.3,
            center_x=self.picture.image_source.center_x - 2)
        anim.start(self.picture.image_source)

    def load_files(self, selection):
        """
        Browsed photo siblings selection, not all but limited ones.
        """
        try:
            file_dir = get_dir(selection)
            self.files = []
            # Selected image action handler
            if os.path.isfile(selection):
                if self.picture.image_source.source != selection:
                    image_source = self.picture.image_source.source
                    if image_source and self.picture.image_name.text:
                        anim = Animation(
                            width=0, t='linear', duration=.3,
                            center_x=self.picture.image_source.center_x + 2
                        )
                        anim.fbind(
                            'on_complete', self.change_image_source, selection
                        )
                        anim.start(self.picture.image_source)
                    else:
                        center_x = self.picture.image_source.center_x

                        self.picture.image_source.width = 0
                        self.selectedimage.path = selection
                        self.selectedimage.name = selection.rsplit("/", 1)[1]
                        self.selectedimage.rotation = 0

                        anim = Animation(
                            width=self.photo.width, t='linear', duration=.3,
                            center_x = center_x - 2
                        )
                        anim.fbind('on_complete', self.activate_buttons)
                        anim.start(self.picture.image_source)
                else:
                    self.selectedimage.path = selection
                    self.selectedimage.name = selection.rsplit("/", 1)[1]
                    self.selectedimage.rotation = 0
                    anim = Animation(
                        width=self.photo.width, t='linear', duration=.3,
                        center_x=self.picture.image_source.center_x + 2
                    )
                    anim.bind(on_complete=self.activate_buttons)
                    anim.start(self.picture.image_source)

            # Files filtered and collect.
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
            # Browser can trace viewed photo
            for item in self.file_chooser._items:
                item.color_selected = get_color_from_hex('B3B3B3')
                if item.path == selection:
                    item.parent.select_node(item)
        except IndexError:
            pass

    def select_source(self, *args):
        """Selected photo action trigger"""
        try:
            selection = args[0][0]
            self.load_files(selection)
        except IndexError:
            pass

    def picturesListed(self, row_index, item):
        """Tracker panel list item handler."""
        return {
            'path': item.get('path', ''),
            'name': item.get('name', ''),
            'rotation': item.get('rotation', 0),
            'is_selected': item.setdefault('is_selected', False)
        }

    def reload_photos(self):
        """
        On photo save, rotation mut be displayed to do reloading
        """
        for pic in self.list_view.children[0].children[0].children:
            im = pic.image_source
            im.reload()
        im = self.picture.image_source

    def _save_photo(self, *args, **kwargs):
        """
        Saving procedure handler.
        """
        rotation_dct = {
            90: Image.ROTATE_90,
            180: Image.ROTATE_180,
            270: Image.ROTATE_270,
        }
        rotation = self.norm_photo(self.photo.rotation, None, None)
        rotation = int(str(rotation).rsplit(".", 1)[0])
        image_path = self.picture.image_source.source
        if rotation > 0 and rotation in rotation_dct:
            im = Image.open(image_path)
            im = im.transpose(rotation_dct.get(rotation))
            im.save(image_path, quality = 95)
            Cache.remove("kv.loader", image_path)
        self.load_files(image_path)
        self.reload_photos()

    def save_photo(self):
        """
        Saving procedure trigger.
        """
        if self.picture.image_source.source and self.picture.image_name.text:
            anim = Animation(
                width=0, t='linear', duration=.3,
                center_x=self.picture.image_source.center_x - 2
            )
            anim.bind(on_complete=self._save_photo)
            anim.start(self.picture.image_source)

    def norm_photo(self, angle, anim, scatter):
        """
        Normalized image rotation
        """
        rotations = [-270, -180, -90, 0, 90, 180, 270]
        find_index = map(lambda x: abs(int(self.photo.rotation) - x), rotations)
        self.selectedimage.rotation = rotations[
            find_index.index(sorted(find_index)[0])]
        return self.photo.rotation

    def rotate(self, angle):
        """
        Rotation handler
        """
        if self.picture.image_source.source and self.picture.image_name.text:
            rotation = self.selectedimage.rotation + angle
            anim = Animation(
                rotation=rotation,
                t='linear', duration=.2)
            anim.fbind('on_complete', self.norm_photo, angle)
            anim.start(self.photo)

    def key_pressed(self, *args, **kwargs):
        """
        Key press action handler.
        """
        try:
            if self.files:
                code = args[1:3]
                next_index = self.selected_index_onlist
                if code in FORWARD_KEY_CODES:
                    next_index = min(
                        self.selected_index_onlist + 1, len(self.files) - 1)
                elif code in BACKWARD_KEY_CODES:
                    next_index = max(self.selected_index_onlist - 1, 0)
                elif code in FULLSCREEN_KEY_CODES:
                    pass
                    # TODO: fullscreen
                    # Window.toggle_fullscreen()
                if next_index != self.selected_index_onlist:
                    self.load_files(self.files[next_index]['path'])
        except IndexError:
            pass

    def set_path(self, *args):
        """
        dropping file trigger all action.
        """
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
        self.path = get_dir(kwargs.get('path'))
        Builder.load_file('assets/PictureViewer.kv')
        self.title = 'Picture Viewer'
        self.icon = 'assets/pictureViewer.icns'

    def build(self):
        pictureviewer = PictureViewer(path=self.path)
        image_source = pictureviewer.picture.image_source.source
        # Save button action handler on start.
        if image_source and pictureviewer.picture.image_name.text:
            pass
        else:
            save_image = pictureviewer.save_but.children[0]
            save_image.source = "assets/trans.png"
        Window.bind(on_key_down=pictureviewer.key_pressed)
        Window.bind(on_dropfile=pictureviewer.set_path)
        return pictureviewer

if __name__ == '__main__':
    import sys
    path = "/Users/denizci/Dropbox/"
    # Tried to take selected photo on start.
    if len(sys.argv) > 1:
        path = sys.argv[1]
    Window.size = 1200, 700
    Window.borderless = False
    Config.set('kivy', 'exit_on_escape', 0)
    Config.set('kivy', 'desktop', 1)
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    PictureViewerApp(path=path).run()
