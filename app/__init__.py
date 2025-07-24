from flask import Flask
from .config import Config
from .extensions import db, migrate, jwt
from flask_cors import CORS
from .auth.routes import auth_bp
from .payments.routes import payments_bp
from .payments.webhooks import webhooks_bp
from .videos.routes import videos_bp
from .downloads.routes import downloads_bp
from .admin.routes import admin_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app, resources={r"/*": {"origins": app.config.get("ALLOWED_ORIGINS", "*").split(",")}})

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(payments_bp, url_prefix="/payments")
    app.register_blueprint(webhooks_bp, url_prefix="/webhooks")
    app.register_blueprint(videos_bp, url_prefix="/videos")
    app.register_blueprint(downloads_bp, url_prefix="/downloads")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.get("/health")
    def health():
        return {"ok": True}

    return app
