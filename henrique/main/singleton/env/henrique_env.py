import os

import yaml
from pathlib import Path

from functools import lru_cache, reduce
from yaml import BaseLoader

from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.jinja2.jinja2_tool import Jinja2Renderer
from foxylib.tools.native.native_tool import BooleanTool
from foxylib.tools.string.string_tool import str2lower

from foxylib.tools.env.env_tool import EnvTool

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)
REPO_DIR = reduce(lambda x,f:f(x), [os.path.dirname]*4, FILE_DIR)

class HenriqueEnv:
    class Key:
        SKIP_WARMUP = "SKIP_WARMUP"
    K = Key

    class Value:
        LOCAL = "local"
        DEV = "dev"
        STAGING = "staging"
        PROD = "prod"


    @classmethod
    def env(cls):
        return cls.env2norm(EnvTool.env_raw())

    @classmethod
    def env2norm(cls, env):
        _env = str2lower(env)

        if _env in {"prod", "production", }:
            return cls.Value.PROD

        if _env in {"staging", }:
            return cls.Value.STAGING

        if _env in {"dev", "develop", "development", }:
            return cls.Value.DEV

        if _env in {"local", }:
            return cls.Value.LOCAL

        raise NotImplementedError(env)

    @classmethod
    def is_skip_warmup(cls):
        nb = cls.key2nullboolean(cls.Key.SKIP_WARMUP)
        return nb is True



    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def _json_yaml(cls, env):
        filepath = os.path.join(REPO_DIR, "henrique", "env", "yaml", "env.henrique.part.yaml")
        if not os.path.exists(filepath):
            return None

        data = {"ENV": env, "HOME_DIR": str(Path.home()), "REPO_DIR": REPO_DIR, }
        utf8 = Jinja2Renderer.textfile2text(filepath, data)
        json_yaml = yaml.load(utf8, Loader=BaseLoader)
        return json_yaml

    @classmethod
    def _env2envs(cls, env):
        __DEFAULT__ = "__DEFAULT__"
        env_norm = cls.env2norm(env)

        if env_norm in {cls.Value.DEV, cls.Value.STAGING, cls.Value.PROD}:
            return [env, __DEFAULT__]

        if env_norm in {cls.Value.LOCAL}:
            return [env, cls.Value.DEV, __DEFAULT__]

        raise NotImplementedError({"env": env})

    @classmethod
    def env_key2value(cls, env, k):
        # return os.environ.get(k)

        json_yaml = cls._json_yaml(env)
        envs = [env, "__DEFAULT__"]
        return EnvTool.json_envs_key2value(json_yaml, envs, k)

    @classmethod
    def key2value(cls, key):
        return cls.env_key2value(cls.env(), key)

    @classmethod
    def key2nullboolean(cls, key):
        v = cls.key2value(key)
        nb = BooleanTool.parse2nullboolean(v)
        return nb

