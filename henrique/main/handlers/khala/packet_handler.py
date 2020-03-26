from henrique.main.singleton.khala.henrique_khala import HenriqueKhala


class PacketHandler:

    @classmethod
    def jinni_uiud2is_matched(cls, jinni_uuid):
        return True


    @classmethod
    def post(cls, packet):
        text = HenriqueKhala.packet2response(packet)
        return text, 200
