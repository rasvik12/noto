from flask import Flask, render_template, request, jsonify
from .config import Config
from .models import db, Note, Tag


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    from .api.notes import notes_bp
    app.register_blueprint(notes_bp)

    # Создаем бд файл, если его нет
    with app.app_context():
        db.create_all() 
    
    @app.route('/')
    def index():
        notes = Note.query.all()
        return render_template('index.html', notes=notes)  # Здесь отдаём index.html
    


    return app