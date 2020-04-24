import os


from foxylib.tools.html.html_tool import wrap_html_tag, join_html_and_wrap
from foxylib.tools.jinja2.jinja2_tool import Jinja2Renderer
from henrique.front.henrique_front import HenriqueFront
from henrique.main.singleton.flask.henrique_urlpath import HenriqueUrlpath

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class AdminSpecialExceptionView:
    @classmethod
    def url(cls):
        return HenriqueUrlpath.obj2url(cls.get)

    @classmethod
    # @app.route(UrlpathTool.filepath_pair2url(FILE_DIR, FRONT_DIR))
    def get(cls):
        raise Exception()
