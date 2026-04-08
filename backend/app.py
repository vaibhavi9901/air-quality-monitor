import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Import and register routes
    from routes.air_quality import air_quality_bp
    from routes.forecast import forecast_bp
    from routes.historical import historical_bp
    from routes.alerts import alerts_bp

    app.register_blueprint(air_quality_bp, url_prefix='/api/air-quality')
    app.register_blueprint(forecast_bp, url_prefix='/api/forecast')
    app.register_blueprint(historical_bp, url_prefix='/api/historical')
    app.register_blueprint(alerts_bp, url_prefix='/api/alerts')

    @app.route('/api/health')
    def health_check():
        return {"status": "healthy", "message": "Backend is running!"}, 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=5001, debug=True)
