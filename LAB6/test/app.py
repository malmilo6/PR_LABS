from flask import Flask
from models.database import db
from flask_swagger_ui import get_swaggerui_blueprint
from models.data import ElectroScooter

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'


def create_app():
    app = Flask(__name__)
    # Configure SQLAlchemy to use SQLite
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'

    # Configure PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:mysecretpassword@localhost:5432/postgres'

    db.init_app(app)

    return app


if __name__ == "__main__":
    app = create_app()
    import routes

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
        API_URL,
        config={  # Swagger UI config overrides
            'app_name': "Test application"
        },
        # oauth_config={  # OAuth config. See https://github.com/swagger-api/swagger-ui#oauth2-configuration .
        #    'clientId': "your-client-id",
        #    'clientSecret': "your-client-secret-if-required",
        #    'realm': "your-realms",
        #    'appName': "your-app-name",
        #    'scopeSeparator': " ",
        #    'additionalQueryStringParams': {'test': "hello"}
        # }
    )

    app.register_blueprint(swaggerui_blueprint)

    app.run()