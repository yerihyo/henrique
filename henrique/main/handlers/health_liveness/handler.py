import os

from flask import request

from foxylib.tools.html.html_tools import join_html


class Handler:
    @classmethod
    def get(cls):
        return "Khala service is healthy based on liveness health check", 200
