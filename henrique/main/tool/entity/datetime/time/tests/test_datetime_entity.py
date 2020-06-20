import logging
from unittest import TestCase

from dateutil import relativedelta

from foxylib.tools.collections.collections_tool import l_singleton2obj
from henrique.main.document.henrique_entity import HenriqueEntity
from henrique.main.tool.entity.datetime.timedelta.timedelta_entity import RelativeTimedeltaEntity


class TestDatetimeEntity(TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)

    def test_01(self):
        config = {HenriqueEntity.Config.Field.LOCALE:"ko"}
        entity_list = RelativeTimedeltaEntity.text2entity_list("+3일", config=config)
        ref = [{'span': (0, 3),
                'text': '+3일',
                'type': 'henrique.main.tool.entity.time.timedelta.timedelta_entity.RelativeTimedeltaEntity',
                'value': {'sign': '+',
                          'timedelta': {'span': (1, 3),
                                        'text': '3일',
                                        'type': 'henrique.main.tool.entity.time.timedelta.timedelta_entity.TimedeltaEntity',
                                        'value': [{'quantity': 3,
                                                   'span': (1, 3),
                                                   'unit': 'day'}]}}}]

        # pprint(hyp)
        self.assertEqual(entity_list, ref)
        self.assertEqual(RelativeTimedeltaEntity.entity2relativedelta(l_singleton2obj(entity_list)),
                         relativedelta.relativedelta(days=3),
                         )

    def test_02(self):
        config = {HenriqueEntity.Config.Field.LOCALE: "ko"}
        entity_list = RelativeTimedeltaEntity.text2entity_list("+20 초", config=config)
        # pprint(entity_list)

        hyp = RelativeTimedeltaEntity.entity2relativedelta(l_singleton2obj(entity_list))
        ref = relativedelta.relativedelta(seconds=20)
        self.assertEqual(hyp, ref)

    def test_03(self):
        config = {HenriqueEntity.Config.Field.LOCALE: "ko"}
        entity_list = RelativeTimedeltaEntity.text2entity_list("-1개월 6일", config=config)
        # pprint(entity_list)

        ref = [{'span': (0, 7),
                'text': '-1개월 6일',
                'type': 'henrique.main.tool.entity.time.timedelta.timedelta_entity.RelativeTimedeltaEntity',
                'value': {'sign': '-',
                          'timedelta': {'span': (1, 7),
                                        'text': '1개월 6일',
                                        'type': 'henrique.main.tool.entity.time.timedelta.timedelta_entity.TimedeltaEntity',
                                        'value': [{'quantity': 1,
                                                   'span': (1, 4),
                                                   'unit': 'month'},
                                                  {'quantity': 6,
                                                   'span': (5, 7),
                                                   'unit': 'day'}]}}}]
        self.assertEqual(entity_list, ref)

        reldelta = RelativeTimedeltaEntity.entity2relativedelta(l_singleton2obj(entity_list))
        reldelta_ref = -1 * relativedelta.relativedelta(months=1, days=6)
        self.assertEqual(reldelta, reldelta_ref)

    def test_04(self):
        config = {HenriqueEntity.Config.Field.LOCALE: "ko"}
        entity_list = RelativeTimedeltaEntity.text2entity_list("-10 mins", config=config)
        # pprint(entity_list)

        hyp = RelativeTimedeltaEntity.entity2relativedelta(l_singleton2obj(entity_list))
        ref = -1 * relativedelta.relativedelta(minutes=10)
        self.assertEqual(hyp, ref)

    def test_05(self):
        config = {HenriqueEntity.Config.Field.LOCALE: "en"}
        entity_list = RelativeTimedeltaEntity.text2entity_list("-10 mins", config=config)
        # pprint(entity_list)

        hyp = RelativeTimedeltaEntity.entity2relativedelta(l_singleton2obj(entity_list))
        ref = -1 * relativedelta.relativedelta(minutes=10)
        self.assertEqual(hyp, ref)

    def test_06(self):
        config = {HenriqueEntity.Config.Field.LOCALE: "en"}
        entity_list = RelativeTimedeltaEntity.text2entity_list("-10분", config=config)
        self.assertFalse(entity_list,)
