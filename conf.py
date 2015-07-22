from kivy.core.text import LabelBase

FILE_EXTENSIONS = []
_ = [FILE_EXTENSIONS.extend((x, x.upper())) for x in ['jpg', 'jpeg', 'png']]

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
