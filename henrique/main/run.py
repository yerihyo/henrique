import logging

from henrique.main.singleton.flask.henrique_flask import HenriqueFlask

logging.basicConfig(level=logging.DEBUG)
app = HenriqueFlask.app()


def main():
    app.run()


if __name__ == '__main__':
    main()

