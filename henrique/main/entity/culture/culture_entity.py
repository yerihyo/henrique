import os
import sys

from functools import lru_cache, partial
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.googleapi.google_api_tool import GoogleAPITool, CredentialCache
from foxylib.tools.googleapi.sheets.googlesheets_tool import GooglesheetsTool
from foxylib.tools.json.json_tool import jdown
from foxylib.tools.json.yaml_tool import YAMLTool
from henrique.main.singleton.cache.henrique_cache import HenriqueCache
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.google.googledoc.henrique_googleapi import HenriqueGoogleapi
from henrique.main.singleton.mongodb.henrique_mongodb import HenriqueMongodb

MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)

class CultureGooglesheets:
    class Sheet:
        class Name:
            NAMES_KO = "names.ko"
            NAMES_EN = "names.en"
            PREFERRED_TRADEGOOD = "preferred_tradegood"

    @classmethod
    def spreadsheetId(cls):
        return "1s_EBQGNu0DlPedOXQNcfmE_LDk4wRq5QgJ9TsdBCCDE"


    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def flow(cls):
        scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly",
                  "https://www.googleapis.com/auth/spreadsheets",
                  ]
        flow = InstalledAppFlow.from_client_secrets_file(HenriqueGoogleapi.filepath_credentials(), scopes)
        return flow

    @classmethod
    def credentials_oauth2(cls):
        cachefile = os.path.join(FILE_DIR, "token.pickle")
        cachefuncs = CredentialCache.filepath2cachefuncs_pickle(cachefile)

        credentials = GoogleAPITool.cache_or_func2cred(cachefuncs, partial(cls.flow().run_local_server, port=0))
        return credentials

    @classmethod
    def credentials_jwt(cls):
        # https://developers.google.com/identity/protocols/oauth2/service-account
        # https://cloud.google.com/docs/authentication/
        return Credentials.from_service_account_file(HenriqueGoogleapi.filepath_privatekey())

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def sheetname2data_ll(cls, sheetname):
        data_ll = GooglesheetsTool.cred_id_name2data_ll(cls.credentials_jwt(), cls.spreadsheetId(), sheetname)
        return data_ll


    @classmethod
    def list_all(cls):
        cachefile = os.path.join(FILE_DIR, "token.pickle")
        cachefuncs = CredentialCache.filepath2cachefuncs_pickle(cachefile)

        credentials = GoogleAPITool.cache_or_func2cred(cachefuncs, partial(cls.flow().run_local_server, port=0))
        sheets = build('sheets', 'v4', credentials=credentials)

        h = {"spreadsheetId": cls.spreadsheetId(),
             "range": sheet_range,
             }
        result = service.spreadsheets().values().get(**h).execute()
        values = result.get('values', [])
        return values



class Culture:


    @classmethod
    def list_all(cls):


        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=youtube_id
        )
        response = request.execute()


        hyp_01 = JsonTool.down(response, ["kind"])
        self.assertEqual(hyp_01, "youtube#videoListResponse")

        item = l_singleton2obj(JsonTool.down(response, ["items"]))

        hyp_02 = JsonTool.down(item, ["id"])
        self.assertEqual(hyp_02, youtube_id)

        hyp_03 = JsonTool.down(item, ["kind"])
        self.assertEqual(hyp_03, "youtube#video")



class CultureCollection:
    COLLECTION_NAME = "culture"

    class YAML:
        NAME = "name"

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def j_yaml(cls):
        filepath = os.path.join(FILE_DIR, "culture_collection.yaml")
        j = YAMLTool.filepath2j(filepath)
        return j

    @classmethod
    def lang2name(cls, lang):
        j_yaml = cls.j_yaml()
        return jdown(j_yaml, [cls.YAML.NAME,lang])

    @classmethod
    def collection(cls, *_, **__):
        db = HenriqueMongodb.db()
        return db.get_collection(cls.COLLECTION_NAME, *_, **__)

class CultureDocument:
    class Field:
        NAME = "name"

        def j_culture_lang2name(cls, j_culture, lang):
            return jdown(j_culture, [lang, cls.NAME])
    F = Field

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=HenriqueCache.DEFAULT_SIZE))
    def name2j_doc(cls, name):
        pass


