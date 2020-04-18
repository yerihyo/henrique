import logging

import connexion

from henrique.main.singleton.flask.henrique_flask import HenriqueFlask


# def create_app():
#     application = connexion.FlaskApp(__name__,)
#     application.add_api('swagger.yaml')
#
#     return application.app

logging.basicConfig(level=logging.DEBUG)
app = HenriqueFlask.app()


def main():
    app.run()
    # ConnectDiscord.run()


if __name__ == '__main__':
    main()

