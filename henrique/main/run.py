import logging

import connexion


def create_app():
    application = connexion.FlaskApp(__name__,)
    application.add_api('swagger.yaml')

    return application.app

logging.basicConfig(level=logging.DEBUG)
app = create_app()


def main():
    app.run()
    # ConnectDiscord.run()


if __name__ == '__main__':
    main()

