import logging
import os

from foxylib.tools.collections.iter_tool import IterTool
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger


class HenriqueWarmer:

    @classmethod
    def warmup_all(cls):
        logger = HenriqueLogger.func_level2logger(cls.warmup_all, logging.DEBUG)
        logger.debug("START")

        # not really necessary cuz warmer will run once loaded in each file, but still to avoid unnecessary warnings
        warmer_list = list(cls.warmer_iter())
        # warmer_list = [IterTool.first(cls.warmer_iter())]
        logger.debug({"warmer_list":warmer_list})
        for x in warmer_list:
            logger.debug({"warmer": x})
            x.warmup()

        logger.debug("END")

    @classmethod
    def warmer_iter(cls):
        logger = HenriqueLogger.func_level2logger(cls.warmer_iter, logging.DEBUG)

        logger.debug("START")

        import khala.singleton.messenger.kakaotalk.internal.chatroom_kakaotalk
        yield khala.singleton.messenger.kakaotalk.internal.chatroom_kakaotalk.WARMER

        import henrique.main.document.skill.skill_entity
        yield henrique.main.document.skill.skill_entity.WARMER

        import henrique.main.singleton.khala.henrique_khala
        yield henrique.main.singleton.khala.henrique_khala.WARMER

        import henrique.main.document.culture.culture_entity
        yield henrique.main.document.culture.culture_entity.WARMER

        import khala.document.channel_user.mongodb.channel_user_doc
        yield khala.document.channel_user.mongodb.channel_user_doc.WARMER

        import henrique.main.skill.price.price_skill
        yield henrique.main.skill.price.price_skill.WARMER

        import henrique.main.document.port.deprecated.port_reference
        yield henrique.main.document.port.deprecated.port_reference.WARMER

        import henrique.main.document.port.port
        yield henrique.main.document.port.port.WARMER

        import henrique.main.document.port.googlesheets.port_googlesheets
        yield henrique.main.document.port.googlesheets.port_googlesheets.WARMER

        import henrique.main.document.tradegood.tradegood_entity
        yield henrique.main.document.tradegood.tradegood_entity.WARMER

        import khala.document.chatroom.mongodb.chatroom_doc
        yield khala.document.chatroom.mongodb.chatroom_doc.WARMER

        import khala.document.channel_user.channel_user
        yield khala.document.channel_user.channel_user.WARMER


        logger.debug("END")


def main():
    HenriqueLogger.attach_stderr2loggers(logging.DEBUG)
    os.environ["SKIP_WARMUP"] = ""
    HenriqueWarmer.warmup_all()


if __name__ == '__main__':
    main()
