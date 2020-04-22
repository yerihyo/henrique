import os


from foxylib.tools.html.html_tool import wrap_html_tag, join_html_and_wrap
from foxylib.tools.jinja2.jinja2_tool import Jinja2Renderer
from henrique.front.henrique_front import HenriqueFront
from henrique.main.singleton.flask.henrique_urlpath import HenriqueUrlpath

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class IndexView:
    @classmethod
    def url(cls):
        return HenriqueUrlpath.obj2url(cls.get)

    @classmethod
    # @app.route(UrlpathTool.filepath_pair2url(FILE_DIR, FRONT_DIR))
    def get(cls):

        html_head = wrap_html_tag(HenriqueFront.html_head_inner(), "head")

        filepath = os.path.join(FILE_DIR, "index.part.html")
        html_body = join_html_and_wrap([HenriqueFront.html_top(),
                                        Jinja2Renderer.htmlfile2markup(filepath),
                                        ], "body")


        # <!DOCTYPE html>
        html = join_html_and_wrap([html_head, html_body], "html",
                                  attrs=HenriqueFront.html_attrs())
        return html, 200
