import os

from markupsafe import Markup

from foxylib.tools.jinja2.jinja2_tool import Jinja2Renderer

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class HenriqueFront:
    @classmethod
    def doctype(cls):
        return Markup("<!DOCTYPE html>")

    @classmethod
    def html_attrs(cls):
        return {"lang": "en"}

    @classmethod
    def dirpath_static(cls):
        return os.path.join(FILE_DIR, "static")

    @classmethod
    def dirpath_singleton(cls):
        return os.path.join(FILE_DIR, "singleton")

    @classmethod
    def html_head_inner(cls):
        filepath = os.path.join(cls.dirpath_singleton(), "head", "head_inner.part.html")
        html_inner = Jinja2Renderer.htmlfile2markup(filepath)
        return html_inner

    @classmethod
    def html_top(cls):
        filepath = os.path.join(cls.dirpath_singleton(), "body", "top", "top.part.html")
        html_inner = Jinja2Renderer.htmlfile2markup(filepath)
        return html_inner
