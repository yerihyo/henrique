import logging
import os

from future.utils import lmap, lfilter

from foxylib.tools.collections.collections_tool import luniq, lchain, smap
from foxylib.tools.collections.iter_tool import IterTool
from foxylib.tools.string.string_tool import str2strip
from henrique.main.document.culture.culture import Culture, Prefer
from henrique.main.document.port.port import Port, Product
from henrique.main.document.tradegood.tradegood import Tradegood
from henrique.main.document.tradegoodtype.tradegoodtype import Tradegoodtype, Tradegoodcategory
from henrique.main.singleton.jinja2.henrique_jinja2 import HenriqueJinja2
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class TradegoodTradegoodResponse:
    @classmethod
    def codename_lang2text(cls, tradegood_codename, lang):
        logger = HenriqueLogger.func_level2logger(cls.codename_lang2text, logging.DEBUG)

        tradegood = Tradegood.codename2tradegood(tradegood_codename)

        filepath = os.path.join(FILE_DIR, "tmplt.{}.part.txt".format(lang))

        tgt_codename = Tradegood.tradegood2tradegoodtype(tradegood)
        tgt = Tradegoodtype.codename2tradegoodtype(tgt_codename) if tgt_codename else None
        category = Tradegoodtype.tradegoodtype2category(tgt) if tgt else None

        ports_selling = Port.tradegood2ports(tradegood_codename)
        prefers = Prefer.tradegood2prefers(tradegood_codename)

        # def prefers2cultures(prefers):
        #     culture_codenames = luniq(map(Prefer.prefer2culture, prefers))
        #     return lmap(Culture.codename2culture, culture_codenames)

        culture_codenames_preferred = luniq(map(Prefer.prefer2culture, prefers)) if prefers else []
        # culture_list_preferred = prefers2cultures(prefers) if prefers else []
        port_list_preferred = lchain(*map(Port.culture2ports, culture_codenames_preferred))

        def port2is_resistant(port):
            if not tgt:
                return False

            products = Product.port2products(Port.port2codename(port))
            tgt_codenames_port = smap(Product.product2tradegoodtype, products)

            logger.debug({"tgt":tgt, "tgt_codenames_port":tgt_codenames_port})
            return Tradegoodtype.tradegoodtype2codename(tgt) in tgt_codenames_port

        port_list_preferred_resistant = lfilter(port2is_resistant, port_list_preferred)

        def ports2str(ports):
            if not ports:
                return None

            return ", ".join([Port.port_lang2name(port, lang) for port in ports])

        def culture_codenames2str(culture_codenames):
            if not culture_codenames:
                return None

            logger.debug({"culture_codenames":culture_codenames})
            cultures = lmap(Culture.codename2culture, culture_codenames)
            return ", ".join([Culture.culture_lang2name(culture, lang) for culture in cultures])

        logger.debug({"culture_codenames_preferred":culture_codenames_preferred})

        data = {"name": Tradegood.tradegood_lang2name(tradegood, lang),
                "category": Tradegoodcategory.tradegoodcategory2str(category) if category else None,
                "tradegoodtype": Tradegoodtype.tradegoodtype_lang2name(tgt, lang) if tgt else None,
                "ports_selling": ports2str(ports_selling),
                "cultures_preferred": culture_codenames2str(culture_codenames_preferred),
                "ports_preferred_resistant": ports2str(port_list_preferred_resistant),
                }
        text_out = str2strip(HenriqueJinja2.textfile2text(filepath, data))

        return text_out

