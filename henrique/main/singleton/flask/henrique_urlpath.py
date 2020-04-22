import os

from foxylib.tools.native.module.module_tool import ModuleTool
from functools import reduce

from foxylib.tools.url.url_tool import UrlpathTool

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)
REPO_DIR = reduce(lambda x,f:f(x), [os.path.dirname]*4, FILE_DIR)


class HenriqueUrlpath:
    @classmethod
    def dirpath_base(cls):
        return os.path.join(REPO_DIR, "henrique", "front", "path")

    @classmethod
    def obj2url(cls, x,):
        filepath = ModuleTool.x2filepath(x)
        dirpath = os.path.dirname(filepath)

        url = UrlpathTool.filepath_pair2url(dirpath, cls.dirpath_base())
        return url

    @classmethod
    def url2json_url(cls, url):
        return ".".join([url, "json"])
