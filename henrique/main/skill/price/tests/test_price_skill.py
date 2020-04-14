import logging
from pprint import pprint
from unittest import TestCase

import pytz
from datetime import datetime, timedelta
from future.utils import lmap

from henrique.main.document.price.mongodb.marketprice_doc import MarketpriceDoc, MarketpriceCollection
from henrique.main.document.price.trend.trend_entity import Trend
from henrique.main.document.server.server import Server
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.skill.price.price_skill import PriceSkill, PriceSkillClique
from khala.document.channel.channel import KakaotalkUWOChannel
from khala.document.channel_user.channel_user import ChannelUser
from khala.document.chatroom.chatroom import KakaotalkUWOChatroom
from khala.document.packet.packet import KhalaPacket

NORM_LIST = PriceSkill.blocks2norm_list_for_unittest
NORM_SET = PriceSkill.blocks2norm_set_for_unittest


class TestPriceSkillClique(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        entities_list = [[{'span': (7, 10), 'text': '리스본', 'value': 'Lisbon', 'type': 'port'}],
                         [{'span': (11, 14), 'text': '육두구', 'value': 'Nutmeg', 'type': 'tradegood'}],
                         ]
        hyp = PriceSkillClique.entities_list2clique(entities_list)
        ref = {'ports': ['Lisbon'], 'tradegoods': ['Nutmeg']}

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_02(self):
        entities_list = [[{'span': (6, 10), 'text': '이베리아', 'value': 'Iberia', 'type': 'culture'}],
                         [{'span': (11, 14), 'text': '육두구', 'value': 'Nutmeg', 'type': 'tradegood'}],
                         ]
        hyp = PriceSkillClique.entities_list2clique(entities_list)
        ref = {'ports': ['Las Palmas',
                         'Faro',
                         'Casablanca',
                         'Gijon',
                         'Palma',
                         'Madeira',
                         'Vianna do Castelo',
                         'Lisbon',
                         'Sagres',
                         'Bilbao',
                         'Seville',
                         'Barcelona',
                         'Porto',
                         'Malaga',
                         'Ceuta',
                         'Montpellier',
                         'Valencia'],
               'tradegoods': ['Nutmeg']}

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_03(self):
        entities_list = [[{'span': (7, 10), 'text': '리스본', 'value': 'Lisbon', 'type': 'port'}],
                         [{'span': (11, 14), 'text': '육두구', 'value': 'Nutmeg', 'type': 'tradegood'}],
                         ]
        hyp = PriceSkillClique.text_entities_list2entities_spans_clique("?price 리스본 육두구", entities_list)
        ref = [(0, 2)]

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_04(self):
        entity_list = [{'span': (7, 10), 'text': '리스본', 'value': 'Lisbon', 'type': 'port'},
                       {'span': (11, 14), 'text': '육두구', 'value': 'Nutmeg', 'type': 'tradegood'},
                       ]
        hyp = PriceSkillClique.text_entity_list2clique_list("?price 리스본 육두구", entity_list)
        ref = [{'ports': ['Lisbon'], 'tradegoods': ['Nutmeg']}]

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_05(self):
        entities_list = [[{'span': (7, 8), 'text': '육', 'value': 'Nutmeg', 'type': 'tradegood'},
                          {'span': (8, 9), 'text': '메', 'value': 'Mace', 'type': 'tradegood'}
                          ],
                         [{'span': (16, 17), 'text': '리스본', 'value': 'Lisbon', 'type': 'port'}],
                         ]
        hyp = PriceSkillClique.entities_list2clique(entities_list)
        ref = {'ports': ['Lisbon'], 'tradegoods': ['Nutmeg', 'Mace']}

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_06(self):
        entity_list = [{'span': (0, 1), 'text': '육', 'value': 'Nutmeg', 'type': 'tradegood'},
                       {'span': (1, 2), 'text': '메', 'value': 'Mace', 'type': 'tradegood'}
                       ]
        hyp = list(PriceSkillClique.entity_list2group_spans("육메", entity_list))
        ref = [(0, 2)]

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_07(self):
        entity_list = [{'span': (7, 10), 'text': '리스본', 'value': 'Lisbon', 'type': 'port'},
                       {'span': (11, 12), 'text': '육', 'value': 'Nutmeg', 'type': 'tradegood'},
                       {'span': (12, 13), 'text': '메', 'value': 'Mace', 'type': 'tradegood'},

                       ]
        hyp = PriceSkillClique.text_entity_list2clique_list("?price 리스본 육메", entity_list)
        ref = [{'ports': ['Lisbon'], 'tradegoods': ['Nutmeg', 'Mace']}]

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_11(self):
        entities_list = [[{'span': (7, 10), 'text': '리스본', 'value': 'Lisbon', 'type': 'port'}],
                         [{'span': (11, 14), 'text': '육두구', 'value': 'Nutmeg', 'type': 'tradegood'}],
                         [{'span': (15, 18), 'text': '120', 'value': 120, 'type': 'rate'}],
                         [{'span': (19, 20), 'text': 'ㅅ', 'value': "rise", 'type': 'trend'}],
                         ]
        hyp = PriceSkillClique.entities_list2clique(entities_list)
        ref = {'ports': ['Lisbon'], 'rate': 120, 'tradegoods': ['Nutmeg'], 'trend': 'rise'}

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_12(self):
        text = "?price 리스본 육두구 120 ㅅ"
        entity_list = [{'span': (7, 10), 'text': '리스본', 'value': 'Lisbon', 'type': 'port'},
                       {'span': (11, 14), 'text': '육두구', 'value': 'Nutmeg', 'type': 'tradegood'},
                       {'span': (15, 18), 'text': '120', 'value': 120, 'type': 'rate'},
                       {'span': (19, 20), 'text': 'ㅅ', 'value': "rise", 'type': 'trend'},
                       ]
        hyp = PriceSkillClique.entity_list2entities_list_grouped(text, entity_list)
        ref = [[{'span': (7, 10), 'text': '리스본', 'value': 'Lisbon', 'type': 'port'}],
               [{'span': (11, 14), 'text': '육두구', 'value': 'Nutmeg', 'type': 'tradegood'}],
               [{'span': (15, 18), 'text': '120', 'value': 120, 'type': 'rate'}],
               [{'span': (19, 20), 'text': 'ㅅ', 'value': "rise", 'type': 'trend'}],
               ]

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_13(self):
        text = "?price 리스본 육두구 120ㅅ"
        entity_list = [{'span': (7, 10), 'text': '리스본', 'value': 'Lisbon', 'type': 'port'},
                       {'span': (11, 14), 'text': '육두구', 'value': 'Nutmeg', 'type': 'tradegood'},
                       {'span': (15, 18), 'text': '120', 'value': 120, 'type': 'rate'},
                       {'span': (18, 19), 'text': 'ㅅ', 'value': "rise", 'type': 'trend'},
                       ]
        hyp = PriceSkillClique.text_entity_list2clique_list(text, entity_list)
        ref = [{'ports': ['Lisbon'], 'rate': 120, 'tradegoods': ['Nutmeg'], 'trend': 'rise'}]

        # pprint(hyp)
        self.assertEqual(hyp, ref)


class TestPriceSkill(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        packet = {KhalaPacket.Field.TEXT: "?price 리스본 육두구",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.CODENAME,
                  }

        hyp = NORM_LIST(PriceSkill.packet2rowsblocks(packet))
        ref = [('[리스본] 시세', {'육두구'})]

        pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_02(self):
        packet = {KhalaPacket.Field.TEXT: "?price 리스본 세비야 육두구 메이스",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.CODENAME,
                  }

        hyp = NORM_SET(PriceSkill.packet2rowsblocks(packet))
        ref = [('[육두구] 시세', {'세비야', '리스본'}),
               ('[메이스] 시세', {'세비야', '리스본'}),
               ]

        # pprint({"hyp":hyp})
        self.assertEqual(hyp, ref)

    def test_03(self):
        packet = {KhalaPacket.Field.TEXT: "?price 육메 이베",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.CODENAME,
                  }

        hyp = NORM_SET(PriceSkill.packet2rowsblocks(packet))
        ref = [('[육두구] 시세',
                {'바르셀로나', '발렌시아', "히혼", "팔마", "빌바오", "세비야", "말라가", "사그레스", "리스본", "세우타", "파루", "라스팔마스", "마데이라",
                 "비아나두카스텔루", "몽펠리에", "카사블랑카", "포르투", }),
               ('[메이스] 시세',
                {'바르셀로나', '발렌시아', "히혼", "팔마", "빌바오", "세비야", "말라가", "사그레스", "리스본", "세우타", "파루", "라스팔마스", "마데이라",
                 "비아나두카스텔루", "몽펠리에", "카사블랑카", "포르투", }),
               ]

        # pprint({"hyp": hyp})
        self.assertEqual(hyp, ref)

    def test_04(self):
        server = "maris"
        ports = ["Lisbon"]
        tradegoods = ["Nutmeg"]

        MarketpriceDoc.server_ports_tradegoods2delete(server, ports, tradegoods)
        # channel = Channel.Codename.KAKAOTALK_UWO_UWO  # discord

        packet = {KhalaPacket.Field.TEXT: "?price 육두구 리스본 120ㅅ",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.CODENAME,
                  KhalaPacket.Field.CHANNEL_USER: KakaotalkUWOChannel.username2channel_user_codename("iris"),
                  KhalaPacket.Field.SENDER_NAME: "iris",
                  }

        ChannelUser.packet2upsert(packet)

        hyp_01 = PriceSkill.packet2response(packet)
        ref_01 = """[육두구] 시세
리스본 120⇗ @ 방금전 [by iris]"""

        #pprint({"hyp_01": hyp_01})
        self.assertEqual(hyp_01, ref_01)

        price_list_latest = MarketpriceDoc.ports_tradegoods2price_list_latest(server, ports, tradegoods)
        hyp_02 = lmap(MarketpriceDoc.doc2norm_unittest, price_list_latest)
        ref_02 = [{'port': 'Lisbon',
                   'rate': 120,
                   'tradegood': 'Nutmeg',
                   'server': 'maris',
                   'trend': 'rise',
                   'channel_user': 'kakaotalk_uwo-iris',
                   }]

        # pprint({"hyp_02": hyp_02})
        self.assertEqual(hyp_02, ref_02)

    def test_05(self):
        dt_now = datetime.now(pytz.utc)

        port = "Lisbon"
        tradegood = "Nutmeg"
        server = Server.Codename.MARIS
        channel_user = 'kakaotalk_uwo-iris'

        def insert_docs():
            collection = MarketpriceCollection.collection()
            doc_old = {MarketpriceDoc.Field.CREATED_AT: dt_now - timedelta(hours=10),
                       MarketpriceDoc.Field.PORT: "Lisbon",
                       MarketpriceDoc.Field.TRADEGOOD: tradegood,
                       MarketpriceDoc.Field.RATE: 120,
                       MarketpriceDoc.Field.TREND: Trend.Value.RISE,

                       MarketpriceDoc.Field.SERVER: server,
                       MarketpriceDoc.Field.CHANNEL_USER: channel_user,
                       }

            doc_new = {MarketpriceDoc.Field.CREATED_AT: dt_now,
                       MarketpriceDoc.Field.PORT: "Seville",
                       MarketpriceDoc.Field.TRADEGOOD: tradegood,
                       MarketpriceDoc.Field.RATE: 60,
                       MarketpriceDoc.Field.TREND: Trend.Value.RISE,

                       MarketpriceDoc.Field.SERVER: server,
                       MarketpriceDoc.Field.CHANNEL_USER: channel_user,
                       }
            collection.insert_many([doc_old, doc_new])

        MarketpriceDoc.server_ports_tradegoods2delete(server, [port], [tradegood])
        insert_docs()


        packet = {KhalaPacket.Field.TEXT: "?price 리스본,세비야 육두구",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.CODENAME,
                  }

        hyp = NORM_LIST(PriceSkill.packet2rowsblocks(packet))
        ref = [('[육두구] 시세', ['세비야', '리스본'])]

        # pprint(hyp)
        self.assertEqual(hyp, ref)
