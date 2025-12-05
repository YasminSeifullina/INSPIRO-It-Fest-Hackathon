from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os
from openai import OpenAI
import math

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key="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")
def fix_nan(value):
    if value is None:
        return ''
    if isinstance(value, float) and math.isnan(value):
        return ''
    return value

def load_university_data():
    try:
        print("Пытаюсь загрузить universities.xlsx...")
        print(os.listdir())  

        df_names = pd.read_excel('universities.xlsx')
        df_data = pd.read_excel('university_data.xlsx')

        print("Файл universities.xlsx загружен:")
        print(df_names.head())

        print("Файл universities_data.xlsx загружен:")
        print(df_data.head())

        universities = []
        for i in range(len(df_names)):
            uni = {
                'id': i,
                'name': fix_nan(df_names.iloc[i, 0] if i < len(df_names) else ''),
                'description': fix_nan(df_data.iloc[i, 1] if i < len(df_data) else ''),
                'specialties': fix_nan(df_data.iloc[i, 2] if i < len(df_data) else ''),
                'website': fix_nan(df_data.iloc[i, 3] if i < len(df_data) else ''),
                'contacts': fix_nan(df_data.iloc[i, 4] if i < len(df_data) else '')
            }

            universities.append(uni)
        
        return universities

    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        return []


universities_data = load_university_data()

def get_chatgpt_info(university_data, info_type):
    """
    Получает информацию от ChatGPT о университете
    info_type: 'general', 'academic', 'admission', 'international'
    """
    prompts = {
        'general': f"Предоставь общую информацию и советы об университете '{university_data['name']}'. Описание: {university_data['description']}. Дай полезные советы для абитуриентов.",
        'academic': f"Расскажи подробно об академических программах университета '{university_data['name']}'. Специальности: {university_data['specialties']}. Опиши преимущества каждого направления.",
        'admission': f"Предоставь подробную информацию о процессе приема и поступления в университет '{university_data['name']}'. Расскажи о требованиях, сроках, документах и советах для поступающих.",
        'international': f"Расскажи о возможностях международного сотрудничества в университете '{university_data['name']}'. Упомяни программы обмена, партнерства, двойные дипломы и международные стажировки."
    }
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": "Ты эксперт по высшему образованию в Казахстане. Предоставляй подробную и полезную информацию для студентов и абитуриентов."},
                {"role": "user", "content": prompts[info_type]}
            ],
            max_tokens=800,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Ошибка OpenAI API: {str(e)}")
        return f"Ошибка получения информации: {str(e)}"

@app.route('/api/universities', methods=['GET'])
def get_universities():
    """Возвращает список всех университетов"""
    search = request.args.get('search', '').lower()
    
    if search:
        filtered = [u for u in universities_data if search in u['name'].lower()]
        return jsonify(filtered)
    
    return jsonify(universities_data)

@app.route('/api/university/<int:uni_id>', methods=['GET'])
def get_university_details(uni_id):
    """Возвращает детальную информацию о университете с данными от ChatGPT"""
    
    if uni_id >= len(universities_data):
        return jsonify({'error': 'Университет не найден'}), 404
    
    university = universities_data[uni_id]
    
    chatgpt_data = {
        'general_info': get_chatgpt_info(university, 'general'),
        'academic_programs': get_chatgpt_info(university, 'academic'),
        'admission_info': get_chatgpt_info(university, 'admission'),
        'international_cooperation': get_chatgpt_info(university, 'international')
    }
    
    response = {
        **university,
        'chatgpt_data': chatgpt_data
    }
    
    return jsonify(response)

@app.route('/api/chat', methods=['POST'])
def chat_with_gpt():
    """Чат с ChatGPT о конкретном университете"""
    data = request.json
    uni_id = data.get('university_id')
    message = data.get('message')
    conversation_history = data.get('history', [])
    
    if uni_id >= len(universities_data):
        return jsonify({'error': 'Университет не найден'}), 404
    
    university = universities_data[uni_id]
    
    system_message = f"""Ты помощник, который отвечает на вопросы о университете '{university['name']}'.

Информация о университете:
- Описание: {university['description']}
- Специальности: {university['specialties']}
- Сайт: {university['website']}
- Контакты: {university['contacts']}

Отвечай подробно, полезно и дружелюбно. Если не знаешь точного ответа, предложи посетить официальный сайт или связаться с приемной комиссией."""
    
    messages = [{"role": "system", "content": system_message}]
    
    for msg in conversation_history:
        messages.append({"role": msg['role'], "content": msg['content']})

    messages.append({"role": "user", "content": message})
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=messages,
            max_tokens=500,
            temperature=0.8
        )
        return jsonify({
            'response': response.choices[0].message.content,
            'role': 'assistant'
        })
    except Exception as e:
        print(f"Ошибка чата: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/compare', methods=['POST'])
def compare_universities():
    """Сравнение двух университетов с помощью ChatGPT"""
    data = request.json
    uni1_id = data.get('university1_id')
    uni2_id = data.get('university2_id')
    
    if uni1_id >= len(universities_data) or uni2_id >= len(universities_data):
        return jsonify({'error': 'Университет не найден'}), 404
    
    uni1 = universities_data[uni1_id]
    uni2 = universities_data[uni2_id]
    
    prompt = f"""Сравни два университета Казахстана по различным критериям:

**Университет 1: {uni1['name']}**
- Описание: {uni1['description']}
- Специальности: {uni1['specialties']}
- Сайт: {uni1['website']}
- Контакты: {uni1['contacts']}

**Университет 2: {uni2['name']}**
- Описание: {uni2['description']}
- Специальности: {uni2['specialties']}
- Сайт: {uni2['website']}
- Контакты: {uni2['contacts']}

Предоставь детальное сравнение по следующим критериям:

1. **Академические программы**: Какие специальности предлагает каждый, сильные стороны
2. **Репутация и история**: Престиж, возраст, достижения
3. **Условия поступления**: Предполагаемые требования и конкурс
4. **Международное сотрудничество**: Возможности обмена и стажировок
5. **Карьерные перспективы**: Для каких карьерных целей подходит каждый
6. **Итоговые рекомендации**: Для кого какой университет лучше подходит

Будь объективным и сбалансированным в оценке."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": "Ты эксперт по высшему образованию, который помогает студентам выбрать лучший университет."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        return jsonify({
            'university1': uni1['name'],
            'university2': uni2['name'],
            'comparison': response.choices[0].message.content
        })
    except Exception as e:
        print(f"Ошибка сравнения: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'universities_loaded': len(universities_data),
        'api': 'OpenAI GPT-3.5-turbo'
    })

if __name__ == '__main__':
    print(f"Загружено университетов: {len(universities_data)}")
    print(f"Используется: OpenAI GPT-3.5-turbo")
    print(f"Сервер запущен на http://localhost:5000")
    app.run(debug=True, port=5000, host='0.0.0.0')