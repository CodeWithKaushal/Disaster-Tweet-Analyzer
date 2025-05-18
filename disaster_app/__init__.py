from flask import Flask
import os
from disaster_app.config import config


def create_app(config_name='default'):
    app = Flask(__name__,
                instance_relative_config=True,
                template_folder=os.path.join(os.path.dirname(
                    os.path.dirname(__file__)), 'templates'),
                static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'))

    # Load the appropriate configuration
    app.config.from_object(config[config_name])

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register blueprints
    from disaster_app.views import main
    app.register_blueprint(main.bp)

    # Register error handlers
    from disaster_app.views import errors
    app.register_blueprint(errors.bp)

    return app
