from flask import Flask, render_template, request, jsonify, render_template_string, redirect, url_for
from .config import Config
from .models import db, Note, Tag
from .api.notes import notes_bp

# Удалить неприлинкованные заметки
def cleanup_unused_tags():
    unused_tags = Tag.query.filter(~Tag.notes.any()).all()
    for tag in unused_tags:
        db.session.delete(tag)
    db.session.commit()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.debug = True

    db.init_app(app)
    # Регистрация маршрутов для API заметок
    from .api.notes import notes_bp
    app.register_blueprint(notes_bp)

    # Регистрация маршрутов для импорта статей
    from .routes.import_article import import_bp
    app.register_blueprint(import_bp, url_prefix='/import')

    # Создаем бд файл, если его нет
    with app.app_context():
        db.create_all() 
    
    # Главная страница
    @app.route('/')
    def index():
        notes = Note.query.all()
        return render_template('index.html', notes=notes)  # Здесь отдаём index.html
    
    @app.route('/notes/create-form', methods=['GET'])
    def get_notes():
            return render_template('create_form.html')  # Здесь отдаём create_form.html

    @app.route('/notes/<id>/delete', methods=['DELETE'])
    def delete_note_on_id(id):
        note = Note.query.get(id)
        if not note:
            return jsonify({'error': 'Note not found'}), 404
        
        db.session.delete(note)
        db.session.commit()

        # Проверим наличие пустых заметок
        unused_tags = Tag.query.filter(~Tag.notes.any()).all()
        for tag in unused_tags:
            db.session.delete(tag)
        db.session.commit()
        cleanup_unused_tags()

        return render_template_string('''
        <div class="note-deleted" 
            hx-get="about:blank"
            hx-trigger="load delay:1500ms"
            hx-swap="delete">
            🗑 Заметка удалена
        </div>
        '''), 200


    # Добавляем новую заметку
    @app.route('/notes/add', methods=['POST'])
    def add_note():
        title = request.form.get('title')
        content = request.form.get('content')
        tags = request.form.get('tags', '').split(',')

        if not title or not content:
            return jsonify({'error': 'Title and content are required'}), 400

        note = Note(title=title, content=content)
        db.session.add(note)
        db.session.commit()

        for tag_name in tags:
            tag_name = tag_name.strip()
            if tag_name:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                note.tags.append(tag)

        db.session.commit()

        # Вернём HTML карточки заметки
        return render_template_string('''
        <div id="note-{{ note.id }}">
        <h3>{{ note.title }}</h3>
        <p>{{ note.content }}</p>
        <p>Теги: {{ note.tags|map(attribute='name')|join(', ') }}</p>
        <button 
            hx-delete="/notes/{{ note.id }}/delete-html" 
            hx-target="#note-{{ note.id }}" 
            hx-swap="outerHTML">
            🗑 Удалить
        </button>
        </div>
        ''', note=note), 201

    # Действие кнопки "Редактировать"
    @app.route('/notes/<id>/edit', methods=['GET'])
    def edit_note(id):
        note = Note.query.get(id)
        if not note:
            return jsonify({'error': 'Note not found'}), 404
        
        return render_template('edit_form.html', note=note)
    
    # Обновление заметки
    @app.route('/notes/<id>/update', methods=['PUT'])
    def update_note(id):
        note = Note.query.get(id)
        if not note:
            return jsonify({'error': 'Note not found'}), 404
        
        title = request.form.get('title')
        content = request.form.get('content')
        tags = request.form.get('tags', '').split(',')

        if not title or not content:
            return jsonify({'error': 'Title and content are required'}), 400

        note.title = title
        note.content = content
        note.tags.clear()  # Удаляем старые теги

        for tag_name in tags:
            tag_name = tag_name.strip()
            if tag_name:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                note.tags.append(tag)

        db.session.commit()

        return render_template_string('''
        <div id="note-{{ note.id }}">
        <h3>{{ note.title }}</h3>
        <p>{{ note.content }}</p>
        <p>Теги: {{ note.tags|map(attribute='name')|join(', ') }}</p>
        <button 
            hx-delete="/notes/{{ note.id }}/delete-html" 
            hx-target="#note-{{ note.id }}" 
            hx-swap="outerHTML">
            🗑 Удалить
        </button>
        </div>
        ''', note=note), 200



    return app