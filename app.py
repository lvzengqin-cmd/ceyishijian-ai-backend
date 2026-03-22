# app.py - Flask主程序
import os
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, TradeLog, AdminUser, generate_webhook_id

app = Flask(__name__)

# 配置
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
# 使用环境变量或根据环境自动选择数据库路径
database_url = os.environ.get('DATABASE_URL')
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # 本地开发使用当前目录，Render使用/data目录
    db_path = '/data/shijian_ai.db' if os.path.exists('/data') else 'shijian_ai.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_EXPIRATION_HOURS'] = 24

# 初始化数据库
db.init_app(app)

# 初始化时创建表
with app.app_context():
    db.create_all()
    
    # 创建默认管理员账户
    admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
    
    if not AdminUser.query.filter_by(username=admin_username).first():
        admin = AdminUser(
            username=admin_username,
            password_hash=generate_password_hash(admin_password),
            is_super_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user created: {admin_username}")

# ============ 工具函数 ============

def generate_token(user_id):
    """生成JWT Token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=app.config['JWT_EXPIRATION_HOURS']),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def decode_token(token):
    """解析JWT Token"""
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Token验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        current_user = User.query.get(payload['user_id'])
        if not current_user:
            return jsonify({'error': 'User not found'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

def admin_required(f):
    """管理员验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('admin_login'))
        
        admin = AdminUser.query.get(session['admin_id'])
        if not admin:
            session.pop('admin_id', None)
            return redirect(url_for('admin_login'))
        
        return f(*args, **kwargs)
    return decorated

# ============ API 接口 ============

@app.route('/api/register', methods=['POST'])
def api_register():
    """用户注册"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Invalid request'}), 400
    
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    device_id = data.get('device_id', '').strip()
    
    if not username or not password or not device_id:
        return jsonify({'error': 'Missing required fields'}), 400
    
    if len(username) < 3 or len(password) < 6:
        return jsonify({'error': 'Username must be at least 3 chars, password at least 6 chars'}), 400
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    # 检查设备ID是否已存在
    existing_user = User.query.filter_by(device_id=device_id).first()
    if existing_user:
        return jsonify({
            'error': 'Device already registered',
            'message': 'This device is already registered. Please login instead.'
        }), 409
    
    # 创建新用户（自动生成Webhook ID）
    new_user = User(
        username=username,
        password_hash=generate_password_hash(password),
        device_id=device_id,
        expire_date=datetime.utcnow() + timedelta(days=7)  # 默认7天试用
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    # 生成Token
    token = generate_token(new_user.id)
    
    return jsonify({
        'success': True,
        'message': 'Registration successful',
        'token': token,
        'user': new_user.to_dict()
    }), 201

@app.route('/api/login', methods=['POST'])
def api_login():
    """用户登录"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Invalid request'}), 400
    
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    device_id = data.get('device_id', '').strip()
    
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    # 更新设备ID（如果提供了且不同）
    if device_id and device_id != user.device_id:
        # 检查新设备ID是否已被其他用户使用
        existing = User.query.filter_by(device_id=device_id).first()
        if existing and existing.id != user.id:
            return jsonify({'error': 'This device is registered to another account'}), 403
        user.device_id = device_id
    
    # 更新登录时间
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # 生成Token
    token = generate_token(user.id)
    
    return jsonify({
        'success': True,
        'token': token,
        'user': user.to_dict()
    })

@app.route('/api/user/info', methods=['GET'])
@token_required
def api_user_info(current_user):
    """获取用户信息"""
    return jsonify({
        'success': True,
        'user': current_user.to_dict()
    })

@app.route('/api/signals', methods=['GET'])
@token_required
def api_signals(current_user):
    """获取交易信号历史"""
    trades = TradeLog.query.filter_by(user_id=current_user.id).order_by(TradeLog.created_at.desc()).limit(50).all()
    
    signals = []
    for trade in trades:
        signals.append({
            'id': trade.id,
            'type': trade.trade_type,
            'amount': trade.amount,
            'symbol': trade.symbol,
            'status': trade.status,
            'message': trade.message,
            'timestamp': int(trade.created_at.timestamp() * 1000)
        })
    
    return jsonify({
        'success': True,
        'signals': signals
    })

# ============ Webhook 接口（接收交易信号） ============

@app.route('/api/webhook/<webhook_id>', methods=['POST'])
def api_webhook(webhook_id):
    """接收交易信号（通过Webhook ID）"""
    # 查找用户
    user = User.query.filter(
        (User.webhook_buy == webhook_id) | (User.webhook_sell == webhook_id)
    ).first()
    
    if not user:
        return jsonify({'error': 'Invalid webhook'}), 404
    
    if not user.is_active:
        return jsonify({'error': 'Account is disabled'}), 403
    
    if user.expire_date and user.expire_date < datetime.utcnow():
        return jsonify({'error': 'Account expired'}), 403
    
    # 判断交易类型
    trade_type = 'buy' if user.webhook_buy == webhook_id else 'sell'
    
    # 获取请求数据
    data = request.get_json() or {}
    amount = data.get('amount', '100')
    symbol = data.get('symbol', 'BTCUSDT')
    
    # 创建交易记录
    trade = TradeLog(
        user_id=user.id,
        trade_type=trade_type,
        amount=amount,
        symbol=symbol,
        status='received',
        message=f'Received {trade_type} signal for {amount} USDT'
    )
    
    db.session.add(trade)
    
    # 更新用户统计
    user.trade_count += 1
    user.last_trade_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'{trade_type.upper()} signal received',
        'trade_id': trade.id
    })

# ============ 管理后台页面 ============

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """管理员登录页面"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        admin = AdminUser.query.filter_by(username=username).first()
        
        if admin and check_password_hash(admin.password_hash, password):
            session['admin_id'] = admin.id
            admin.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
        
        flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/admin/logout')
def admin_logout():
    """管理员登出"""
    session.pop('admin_id', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """管理后台首页"""
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'expired_users': User.query.filter(User.expire_date < datetime.utcnow()).count(),
        'today_trades': TradeLog.query.filter(
            TradeLog.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
        ).count(),
        'total_trades': TradeLog.query.count()
    }
    
    # 最近注册用户
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    # 最近交易
    recent_trades = TradeLog.query.order_by(TradeLog.created_at.desc()).limit(10).all()
    
    return render_template('dashboard.html', 
                          stats=stats, 
                          recent_users=recent_users,
                          recent_trades=recent_trades)

@app.route('/admin/users')
@admin_required
def admin_users():
    """用户管理页面"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    users = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('users.html', users=users)

@app.route('/admin/user/<int:user_id>')
@admin_required
def admin_user_detail(user_id):
    """用户详情页面"""
    user = User.query.get_or_404(user_id)
    trades = TradeLog.query.filter_by(user_id=user.id).order_by(TradeLog.created_at.desc()).limit(50).all()
    
    return render_template('user_detail.html', user=user, trades=trades)

@app.route('/admin/api/user/<int:user_id>/webhooks', methods=['GET'])
@admin_required
def admin_get_webhooks(user_id):
    """获取用户的Webhook链接（API）"""
    user = User.query.get_or_404(user_id)
    
    base_url = request.url_root.rstrip('/')
    
    return jsonify({
        'success': True,
        'user_id': user.id,
        'username': user.username,
        'webhook_buy': f"{base_url}/api/webhook/{user.webhook_buy}",
        'webhook_sell': f"{base_url}/api/webhook/{user.webhook_sell}"
    })

@app.route('/admin/api/user/<int:user_id>/extend', methods=['POST'])
@admin_required
def admin_extend_user(user_id):
    """延长用户会员期限"""
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}
    days = data.get('days', 30)
    
    if user.expire_date and user.expire_date > datetime.utcnow():
        user.expire_date = user.expire_date + timedelta(days=days)
    else:
        user.expire_date = datetime.utcnow() + timedelta(days=days)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Membership extended by {days} days',
        'new_expire_date': user.expire_date.isoformat()
    })

# ============ 健康检查 ============

@app.route('/health')
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat()
    })

# ============ 主页 ============

@app.route('/')
def index():
    """首页"""
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)