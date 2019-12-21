from flask_login import current_user
from libgravatar import Gravatar


def get_avatar():
    g = Gravatar(current_user.email)
    return g.get_image(size=84, default='mm')
