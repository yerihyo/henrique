import logging

from henrique.main.singleton.logger.henrique_logger import HenriqueLogger


class HenriqueWarmup:

    @classmethod
    def warmup_all(cls):
        logger = HenriqueLogger.func_level2logger(cls.warmup_all, logging.DEBUG)
        logger.debug("START")

        # not really necessary cuz warmer will run once loaded in each file, but still to avoid unnecessary warnings
        for x in cls.warmer_iter():
            logger.debug({"warmer": x})
            x.warmup()

        logger.debug("END")

    @classmethod
    def warmer_iter(cls):
        logger = HenriqueLogger.func_level2logger(cls.warmup_all, logging.DEBUG)

        logger.debug("START")

        import henrique.main.document.culture.culture_entity
        yield henrique.main.document.culture.culture_entity.WARMER

        logger.debug("END")
