from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

# Создаем объект базы данных
db = SQLAlchemy()

# Промежуточная таблица для связи Note <-> Tag
note_tags = db.Table('note_tags',
                     db.Column('note_id', db.Integer, db.ForeignKey('note.id'), primary_key = True),
                     db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key = True)
                     )

# Модель заметки
class Note(db.Model):
    # Название таблицы
    __tablename__ = 'note'

    # Колонки (id, Заголовок, Контент, Дата-время)
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(200), nullable = False)
    content = db.Column(db.Text, nullable = False)
    created_at = db.Column(db.DateTime, default = lambda:datetime.now(timezone.utc))

    # Связь с тегами (многое-ко-многим)
    tags = db.relationship('Tag', secondary = note_tags, back_populates = 'notes')

    def __repr__(self):
        return f"<Note {self.title}>"
    
# Модель тега
class Tag(db.Model):
    __tablename__ = 'tag'

    # Колонки таблицы (id, название тега)
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), unique = True, nullable = False)

    # Связь с заметками
    notes = db.relationship('Note', secondary = note_tags, back_populates = 'tags')

    def __repr__(self):
        return f"<Tag {self.name}>"
    