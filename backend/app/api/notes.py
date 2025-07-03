from flask import Blueprint, request, jsonify
from ..models import db, Note, Tag

notes_bp = Blueprint('notes_bp', __name__, url_prefix = '/api/notes')

# Удалить неприлинкованные заметки
def cleanup_unused_tags():
    unused_tags = Tag.query.filter(~Tag.notes.any()).all()
    for tag in unused_tags:
        db.session.delete(tag)
    db.session.commit()


# Получить все заметки
@notes_bp.route('/', methods = ['GET'])
def get_notes():
    tag_name = request.args.get('tag')  # Получаем параметр tag из query string
    if tag_name:
        notes = Note.query.join(Note.tags).filter(Tag.name == tag_name).all()
    else:
        notes = Note.query.all()
    result = []
    for note in notes:
        result.append({
            'id': note.id,
            'title': note.title,
            'content': note.content,
            'tags':[tag.name for tag in note.tags]
        })
    return jsonify(result), 200

# Получить одну заметку
@notes_bp.route('/<int:note_id>', methods = ['GET'])
def get_note_on_id(note_id):
    note = Note.query.get(note_id)
    if not note:
        return jsonify({'error': 'Note not found'}), 404
    result = {'id': note.id,
            'title': note.title,
            'content': note.content,
            'tags':[tag.name for tag in note.tags]
               }
    return jsonify(result), 200


# Удалить заметку по ID
@notes_bp.route('/<int:note_id>', methods = ['DELETE'])
def delete_note_on_id(note_id):
    note = Note.query.get(note_id)
    if not note:
        return jsonify({'error': 'Note not found'}), 404
    
    db.session.delete(note)
    db.session.commit()

    # Проверим наличие пустых заметок
    cleanup_unused_tags()
    return jsonify({'message': 'Note is deleted'}), 200


# Обновление заметки
@notes_bp.route('/<int:note_id>', methods = ['PUT'])
def update_note_on_id(note_id):
    note = Note.query.get(note_id)
    if not note:
        return jsonify({'error': 'Note not found'}), 404
    

    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    tags_name = data.get('tags',[])

    if not title or not content:
        return jsonify({'error': 'Title and content required'}), 400
    
    # Обновляем поля существующей заметки
    note.title = title
    note.content = content

    # Обновляем теги: очищаем старые
    note.tags.clear()

    # Обработка тегов: ищем или создаем
    for tag_name in tags_name:
        tag = Tag.query.filter_by(name = tag_name).first()
        if not tag:
            tag = Tag(name = tag_name)
        note.tags.append(tag)
    
    db.session.commit()
    return jsonify({'message' : 'Note updated', 'id': note.id}), 200


# Создать заметку
@notes_bp.route('/', methods=['POST'])
def create_note():
    if not request.is_json:
        data = request.form.to_dict()
        data['tags'] = [t.strip() for t in data.get('tags', '').split(',') if t.strip()]
    else:
        data = request.get_json()

    title = data.get('title')
    content = data.get('content')
    tags_name = data.get('tags', [])

    if not title or not content:
        return jsonify({'error': 'Title and content required'}), 400
    
    note = Note(title = title, content = content)

    # Обработка тегов: ищем или создаем
    for tag_name in tags_name:
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name = tag_name)
        note.tags.append(tag)
    
    db.session.add(note)
    db.session.commit()

    
    # Проверим наличие пустых заметок
    cleanup_unused_tags()

    return jsonify({'message': 'Note created', 'id' : note.id}), 201


