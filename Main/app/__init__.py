from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    CORS(app)

    # Register the routes blueprint
    from .routes import routes
    app.register_blueprint(routes)

    return app
