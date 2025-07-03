# backend/app/routes/import.py
from flask import Blueprint, request, render_template_string
from readability import Document  # легкая библиотека для парсинга
import requests
from bs4 import BeautifulSoup     # для fallback обработки, если нужно

import_bp = Blueprint('import_bp', __name__)

@import_bp.route('/article', methods=['POST'])
def import_article():
    url = request.form.get('url')  # Получаем URL из формы
    # Проверяем, что URL указан
    print(f"Импортируемая ссылка: {url}")
    if not url:
        return render_template_string('<p>Ошибка: ссылка не указана</p>'), 400

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Cookie': 'c-jR0Irvz0KO4GIlv6rbdYz2ZpC3z1R0Wkaw=; c-jR0Irvz0KO4GIlv6rbdYz2ZpC3z1R0Wkaw=; OAID=5968dd9599776d6e05fc607dfe8a1c5a',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            }
        print(f"Загружаем HTML с {url}...")
        # Загружаем HTML страницы
        response = requests.get(url, headers=headers, timeout=10)
        # Проверяем успешность запроса
        if response.status_code != 200:
            print(f"Ошибка при загрузке страницы: {response.status_code}")
        response.raise_for_status()
        html = response.text
        print(f"Получен HTML: {html[:100]}...")  # Выводим первые 100 символов HTML для отладки

        # Используем readability для извлечения заголовка и текста
        doc = Document(html)
        title = doc.title()
        summary_html = doc.summary()  # HTML-резюме основного контента

        # Парсим summary через BeautifulSoup, чтобы достать только текст
        soup = BeautifulSoup(summary_html, 'html.parser')
        content = soup.get_text("\n", strip=True)

        # Возвращаем форму создания заметки с заполненными полями
        return render_template_string('''
        <h2>Импортированная статья</h2>
        <form 
          hx-post="/notes/add" 
          hx-target="#content" 
          hx-swap="innerHTML">
            <label>Заголовок:<br><input type="text" name="title" value="{{ title }}" required></label><br>
            <label>Контент:<br><textarea name="content" required>{{ content }}</textarea></label><br>
            <label>Теги (через запятую):<br><input type="text" name="tags"></label><br>
            <button type="submit">Сохранить</button>
        </form>
        ''', title=title, content=content)

    except Exception as e:
        return render_template_string(f'<p>Не удалось импортировать статью: {str(e)}</p>'), 500
