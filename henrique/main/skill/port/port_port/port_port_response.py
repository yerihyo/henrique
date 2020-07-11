import logging
import os
from random import choice

from future.utils import lmap

from foxylib.tools.collections.collections_tool import luniq
from foxylib.tools.collections.iter_tool import IterTool
from foxylib.tools.string.string_tool import str2strip
from henrique.main.document.culture.culture import Culture
from henrique.main.document.port.port import Product
from henrique.main.document.port.port_entity import Port
from henrique.main.document.tradegoodtype.tradegoodtype import Tradegoodtype
from henrique.main.singleton.jinja2.henrique_jinja2 import HenriqueJinja2
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class PortPortResponse:
    @classmethod
    def codename_lang2text(cls, port_codename, lang):
        logger = HenriqueLogger.func_level2logger(cls.codename_lang2text, logging.DEBUG)

        port = Port.codename2port(port_codename)
        culture = Culture.codename2culture(Port.port2culture(port))

        tgt_codenames = luniq(filter(bool, map(Product.product2tradegoodtype, Product.port2products(port_codename))))
        tradegoodtype_list = sorted(map(Tradegoodtype.codename2tradegoodtype, tgt_codenames), key=Tradegoodtype.key)

        def tgt_list2text_resistant(tgt_list):
            logger.debug({"tgt_list":tgt_list})

            if not tgt_list:
                return None

            return ", ".join([Tradegoodtype.tradegoodtype_lang2name(tgt, lang) for tgt in tgt_list])

        tradegoodtypes_resistant = tgt_list2text_resistant(tradegoodtype_list)

        comments = Port.port_lang2comments(port, lang)
        comment = choice(comments) if comments else None

        filepath = os.path.join(FILE_DIR, "tmplt.{}.part.txt".format(lang))
        data = {"name": Port.port_lang2name(port, lang),
                "culture": Culture.culture_lang2name(culture,lang),
                "tradegoodtypes_resistant":tradegoodtypes_resistant,
                "comment":comment,
                }
        text_out = str2strip(HenriqueJinja2.textfile2text(filepath, data))

        return text_out

