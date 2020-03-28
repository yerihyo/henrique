import os

from functools import reduce

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)
REPO_DIR = reduce(lambda x, f: f(x), [os.path.dirname] * 5, FILE_DIR)


class HenriqueGoogleapi:
    @classmethod
    def email(cls):
        return "foxytrixy@henrique-272420.iam.gserviceaccount.com"

    @classmethod
    def filepath_credentials(cls):
        return os.path.join(FILE_DIR, "credentials.json")

    @classmethod
    def filepath_privatekey(cls):
        # http://console.cloud.google.com/iam-admin/serviceaccounts/details/112472142364049649520
        return os.path.join(REPO_DIR, "env", "google", "api", "henrique-272420-c09c9b3e31ff.json")

    # @classmethod
    # def project_id(cls):
    #     return "henrique-272420"
    #
    # @classmethod
    # def algorithm(cls):
    #     return "RS256"

    # @classmethod
    # def private_key_file(cls):
    #     return os.path.join(FILE_DIR, "henrique-272420-2fbbcb4032da.json")

    # @classmethod
    # def jwt(cls):
    #     return GoogleapiJWT.create_jwt(cls.project_id(), cls.private_key_file(), cls.algorithm())

    # @classmethod
    # def credentials(cls):
    #     scopes = ["https://www.googleapis.com/auth/spreadsheets",
    #               # "https://www.googleapis.com/auth/youtube.readonly",
    #               ]
    #
    #     cachefile = os.path.join(FILE_DIR, "token.pickle")
    #
    #     # os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" # done by environment variable
    #     flowrun = GoogleAPITool.file_scope2flowrun_local_server(cls.filepath_credentials(), scopes, )
    #     credentials = GoogleAPITool.flowrun_cachefile2credentials(partial(flowrun, port=0), cachefile)
    #     return credentials

