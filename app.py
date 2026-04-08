"""
Air Quality Alert System — Flask Backend
"""

from flask import Flask
from flask_cors import CORS
from config import Config


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Import db INSIDE create_app so there is only ever one instance
    # and init_app is always called before anything else touches the DB
    from database.models import db
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    with app.app_context():
        db.create_all()

    # Register blueprints
    from routes.air_quality import air_quality_bp
    from routes.forecast    import forecast_bp
    from routes.historical  import historical_bp
    from routes.alerts      import alerts_bp
    from routes.cities      import cities_bp

    app.register_blueprint(air_quality_bp, url_prefix="/api/air-quality")
    app.register_blueprint(forecast_bp,    url_prefix="/api/forecast")
    app.register_blueprint(historical_bp,  url_prefix="/api/historical")
    app.register_blueprint(alerts_bp,      url_prefix="/api/alerts")
    app.register_blueprint(cities_bp,      url_prefix="/api/cities")

    @app.get("/")
    def health_check():
        return {"status": "ok", "service": "Air Quality Alert System"}

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

# """
# Air Quality Alert System — Flask Backend
# Malaysia-focused, using WAQI API + OpenDOSM historical datasets.
# """

# from flask import Flask
# from flask_cors import CORS
# from config import Config
# from routes.air_quality import air_quality_bp
# from routes.forecast import forecast_bp
# from routes.historical import historical_bp
# from routes.alerts import alerts_bp

# def create_app(config_class=Config) -> Flask:
#     app = Flask(__name__)
#     app.config.from_object(config_class)

#     # Enable CORS for all origins (tighten in production)
#     CORS(app, resources={r"/api/*": {"origins": "*"}})

#     # Register blueprints
#     app.register_blueprint(air_quality_bp, url_prefix="/api/air-quality")
#     app.register_blueprint(forecast_bp,    url_prefix="/api/forecast")
#     app.register_blueprint(historical_bp,  url_prefix="/api/historical")
#     app.register_blueprint(alerts_bp,      url_prefix="/api/alerts")

#     @app.get("/")
#     def health_check():
#         return {"status": "ok", "service": "Air Quality Alert System"}

#     return app


# if __name__ == "__main__":
#     app = create_app()
#     app.run(debug=True, host="0.0.0.0", port=5000)
