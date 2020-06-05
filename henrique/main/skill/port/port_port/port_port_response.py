import logging
import os
from random import choice

from foxylib.tools.collections.collections_tool import luniq
from future.utils import lmap, lfilter

from foxylib.tools.collections.iter_tool import IterTool
from foxylib.tools.native.native_tool import is_not_none
from foxylib.tools.string.string_tool import str2strip
from henrique.main.document.culture.culture import Culture
from henrique.main.document.port.port import Product
from henrique.main.document.port.port_entity import Port
from henrique.main.document.tradegood.tradegood import Tradegood
from henrique.main.document.tradegoodtype.tradegoodtype import Tradegoodtype
from henrique.main.singleton.jinja2.henrique_jinja2 import HenriqueJinja2
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class PortPortResponse:
    @classmethod
    def port2tradegoodtypes_resistant(cls, port):
        logger = HenriqueLogger.func_level2logger(cls.port2tradegoodtypes_resistant, logging.DEBUG)

        product_list = Port.port2products(port)
        if not product_list:
            return []

        tradegood_list = lmap(lambda tg: Tradegood.codename2tradegood(Product.product2tradegood(tg)), product_list)

        def tg2tgt(tg):
            tgt_codename = Tradegood.tradegood2tradegoodtype(tg)
            if not tgt_codename:
                return None

            tgt = Tradegoodtype.codename2tradegoodtype(tgt_codename)
            logger.debug({"tgt_codename":tgt_codename,
                          "tgt":tgt,
                          })
            return tgt

        def tg_list2tgt_list(tg_list):
            tgt_iter = filter(is_not_none, map(tg2tgt, tg_list))
            return sorted(IterTool.uniq(tgt_iter, idfun=Tradegoodtype.key),key=Tradegoodtype.key)

        tradegoodtype_list = tg_list2tgt_list(tradegood_list)
        return tradegoodtype_list

    @classmethod
    def codename_lang2text(cls, port_codename, lang):
        port = Port.codename2port(port_codename)
        culture = Culture.codename2culture(Port.port2culture(port))

        tradegoodtype_list = cls.port2tradegoodtypes_resistant(port)

        def tgt_list2text_resistant(tgt_list):
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

