u"""Picture Viewer Kivy source code."""
__version__ = '1.0.0'

import os
import webbrowser
from urllib2 import urlopen
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
    StringProperty, BooleanProperty,
    ListProperty, NumericProperty
)

from kivy.clock import Clock
from kivy.cache import Cache
from kivy.utils import get_color_from_hex
from kivy.animation import Animation
from conf import (
    FILE_EXTENSIONS, FORWARD_KEY_CODES,
    BACKWARD_KEY_CODES, FULLSCREEN_KEY_CODES
)


def get_dir(path):
    """Find dirname of given path."""
    file_dir = os.path.dirname(path)
    return file_dir


def open_page(*args):
    """To download new version download page opened."""
    webbrowser.open(args[0])


class ImageSelectButton(ToggleButton, ToggleButtonBehavior):

    """Extended version of togglebutton class to trace images on right pane."""

    selected = {'down': 'DDDDDD',
                'normal': 'F5F5F5'}

    def change_color(self):
        """Selected image on right sided panel must be recognized."""
        self.background_color = get_color_from_hex(self.selected[self.state])

    def select(self):
        """Selected image on right sided panel should be main photo."""
        pictureviewer = self.parent.parent.parent.parent.parent
        pictureviewer.load_files(self.parent.path)

    def deselect(self, *args, **kwargs):
        """Super class built-in deselect method."""
        pass

    def _do_press(self):
        """To handle button pressure on right sided panel."""
        buttons = ToggleButtonBehavior.get_widgets('images')
        for button in buttons:
            if self != button:
                button.state = 'normal'
                button.is_select = False
            else:
                button.state = 'down'
                button.is_select = True
            button.change_color()


class Pictures(GridLayout):

    """Selected image handler."""

    path = StringProperty('')
    name = StringProperty('')
    rotation = NumericProperty(0)
    is_selected = BooleanProperty(False)


class PictureViewer(GridLayout):

    """Main class as viewed."""

    source = StringProperty("")
    files = ListProperty([])
    selected_index_onlist = NumericProperty(0)
    selectedimage = Pictures()

    def __init__(self, *args, **kwargs):
        """Initial function."""
        self.filters = ["*.%s" % ext for ext in FILE_EXTENSIONS]
        self.path = kwargs.pop('path')
        super(PictureViewer, self).__init__(*args, **kwargs)
        self.check_update(call=True)

    def check_update(self, call=False):
        """Version control handler."""
        if not call:
            resp = urlopen(
                "https://github.com/RedXBeard/PictureViewer/releases/latest")
            version_text = "".join(resp.url.rsplit("/", 1)[1].split("."))
            if not version_text.isdigit():
                current_version = 0
            else:
                current_version = int(version_text)

            if current_version > int("".join(__version__.split('.'))):
                info_text = "[color=FF4545]"
                info_text += "Newer Version Released please check[/color]"
                info_text += "[color=3148F5][i]"
                info_text += "[ref=https://github.com/RedXBeard/PictureViewer]"
                info_text += "PictureViewer[/ref][/i][/color]"
                self.info.text = info_text
                self.info.bind(on_ref_press=open_page)
        Clock.schedule_once(lambda dt: self.check_update(), 3600)

    def change_item_colors(self):
        """Selection traced also on right sided panel."""
        for item in self.file_chooser._items:
            item.color_selected = get_color_from_hex('B3B3B3')

    def browser_action_handler(self, button, animation=None, weakref=None):
        """close and display browser panel action handled."""
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
                            wwidget.text = step == 0 and 'Size' or 'Name'
                            step += 1

    def browser_action(self, button):
        """close and display browser panel action trigger."""
        if button.direction == "left":
            anim = Animation(width=0, d=.2, t='linear')
        else:
            anim = Animation(width=250, d=.2, t='linear')
        anim.fbind('on_complete', self.browser_action_handler, button)
        anim.start(self.file_chooser)

    def tracker_action_handler(self, button, animation=None, weakref=None):
        """Close and display tracker panel action handled."""
        if button.direction == "left":
            button.direction = "right"
            button.text = "[font=assets/fontawesome-webfont.ttf][/font]"
        else:
            button.direction = "left"
            button.text = "[font=assets/fontawesome-webfont.ttf][/font]"

    def tracker_action(self, button):
        """Close and display tracker panel action trigger."""
        if button.direction == "right":
            anim = Animation(width=0, d=.2, t='linear')
        else:
            anim = Animation(width=150, d=.2, t='linear')
        anim.fbind('on_complete', self.tracker_action_handler, button)
        anim.start(self.list_view)

    def activate_buttons(self, animation=None, weakref=None):
        """Action buttons comes inactive must activated with selection."""
        self.rotate_left.text = self.rotate_left.pre_text
        self.rotate_right.text = self.rotate_right.pre_text
        save_image = self.save_but.children[0]
        save_image.source = "assets/save_icon.png"

    def change_image_source(self, img_path, animation=None, weakref=None):
        """Selected image action main handler."""
        self.selectedimage.path = img_path
        self.selectedimage.name = img_path.rsplit("/", 1)[1]
        self.selectedimage.rotation = 0
        self.activate_buttons()
        anim = Animation(width=self.photo.width, t='linear', duration=.2,
                         center_x=self.picture.image_source.center_x - 2)
        anim.start(self.picture.image_source)

    def load_files(self, selection):
        """Browsed photo siblings selection, not all but limited ones."""
        try:
            file_dir = get_dir(selection)
            self.files = []
            # Selected image action handler
            if os.path.isfile(selection):
                if self.picture.image_source.source != selection:
                    image_source = self.picture.image_source.source
                    if image_source and self.picture.image_name.text:
                        anim = Animation(
                            width=0, t='linear', duration=.2,
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
                            width=self.photo.width, t='linear', duration=.2,
                            center_x=center_x - 2
                        )
                        anim.fbind('on_complete', self.activate_buttons)
                        anim.start(self.picture.image_source)
                else:
                    self.selectedimage.path = selection
                    self.selectedimage.name = selection.rsplit("/", 1)[1]
                    self.selectedimage.rotation = 0
                    anim = Animation(
                        width=self.photo.width, t='linear', duration=.2,
                        center_x=self.picture.image_source.center_x + 2
                    )
                    anim.bind(on_complete=self.activate_buttons)
                    anim.start(self.picture.image_source)

            # Files filtered and collect.
            selected = {}
            for ext in FILE_EXTENSIONS:
                files = glob("%s/*.%s" % (file_dir, ext))
                for f_path in files:
                    tmp = {
                        'name': f_path.rsplit("/", 1)[1],
                        'path': f_path,
                        'is_selected': selection == f_path and True or False,
                        'rotation': 0
                    }
                    self.files.append(tmp)
                    if tmp['is_selected']:
                        selected = tmp
            self.files = sorted(self.files, key=lambda x: x.get('path'))
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

    def select_source(self, img_paths):
        """Selected photo action trigger"""
        try:
            selection = img_paths[0]
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
        im.reload()

    def save_photo_handler(self, animation=None, weakref=None):
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
            im.save(image_path, quality=95)
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
            anim.bind(on_complete=self.save_photo_handler)
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

    def key_pressed(self, *args):
        """
        Key press action handler.
        """
        print "barbaros", args, kwargs
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
    path = "/"
    # Tried to take selected photo on start.
    if len(sys.argv) > 1:
        path = sys.argv[1]
    Window.size = 1200, 700
    Window.borderless = False
    Config.set('kivy', 'exit_on_escape', 0)
    Config.set('kivy', 'desktop', 1)
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    PictureViewerApp(path=path).run()

Cc: pep8 pylint checker <barbarosaliyildirimATgmailDOTcom>
Cc: Barbaros Yıldırım <barbarosaliyildirimATgmailDOTcom>
