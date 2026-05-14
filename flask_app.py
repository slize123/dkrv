import os
import json
import sqlite3
import secrets
import time
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# Путь к файлу базы данных
DB_PATH = 'licenses.db'
DATA_DIR = '.'

def init_db():
    """Создаёт таблицу для ключей, если её ещё нет."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS licenses
                 (key TEXT PRIMARY KEY,
                  hwid TEXT,
                  expires INTEGER,
                  activated_at INTEGER,
                  status TEXT)''')
    conn.commit()
    conn.close()

def generate_key_for_hwid(hwid, expire_days=30):
    """Генерирует новый ключ, привязанный к HWID."""
    prefix = "DRK"
    expires = int(time.time()) + (expire_days * 86400)
    exp_str = time.strftime("%Y%m%d%H%M", time.gmtime(expires))

    # Контрольная сумма (защита от подделки)
    secret = "DarkRvankaSecret2026"
    data = hwid + "|" + exp_str + "|" + secret
    import hashlib
    checksum = hashlib.sha256(data.encode()).hexdigest()[:8].upper()

    key = f"{prefix}-{exp_str}-{hwid[:16]}-{checksum}"

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO licenses (key, hwid, expires, status) VALUES (?, ?, ?, ?)",
              (key, hwid, expires, 'unused'))
    conn.commit()
    conn.close()
    return key

@app.route('/')
def home():
    return jsonify({"status": "running", "message": "Dark Rvanka License API is active"})

@app.route('/api/activate', methods=['POST'])
def activate():
    data = request.get_json()
    key = data.get('key', '').strip().upper()
    hwid = data.get('hwid', '')

    # В реальной активации здесь будет проверка
    # Этот эндпоинт используется твоим Lua скриптом

    # Пример проверки (на самом деле ты уже написал эту логику в Lua)
    # Поэтому здесь я показываю заглушку. Ты можешь вставить сюда свою логику из предыдущих версий.

    # Сейчас просто возвращаем успех для теста
    return jsonify({"success": True, "expires": int(time.time() + 30*86400)})

@app.route('/api/verify', methods=['POST'])
def verify():
    data = request.get_json()
    key = data.get('key', '').strip().upper()
    hwid = data.get('hwid', '')

    # Проверка ключа
    # Здесь будет твоя логика. Сейчас для теста — всегда успешно
    return jsonify({"success": True, "expires": int(time.time() + 30*86400)})

# Маршрут для генерации ключей (доступен только админу)
@app.route('/makekey/<int:days>')
def makekey(days):
    # Простая защита — только для теста. На реальном проекте нужно добавить авторизацию!
    hwid = request.args.get('hwid', '')
    if not hwid:
        return "❌ Укажите HWID через параметр hwid, например: /makekey/30?hwid=ВАШ_HWID"
    key = generate_key_for_hwid(hwid, days)
    return f"✅ Ключ создан!\nHWID: {hwid}\nСрок: {days} дней\nКлюч: {key}"

# Инициализация базы данных
init_db()

# Для локального запуска
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
