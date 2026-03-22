# models.py - 数据库模型
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import secrets
import string

db = SQLAlchemy()

def generate_webhook_id():
    """生成随机Webhook ID"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    device_id = db.Column(db.String(256), unique=True, nullable=False)
    
    # Webhook ID（自动生成，用户不可见）
    webhook_buy = db.Column(db.String(64), unique=True, nullable=False, default=generate_webhook_id)
    webhook_sell = db.Column(db.String(64), unique=True, nullable=False, default=generate_webhook_id)
    
    # 会员信息
    expire_date = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # 交易统计
    trade_count = db.Column(db.Integer, default=0)
    last_trade_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        """返回用户信息（不包含敏感数据）"""
        return {
            'id': self.id,
            'username': self.username,
            'device_id': self.device_id,
            'expire_date': self.expire_date.isoformat() if self.expire_date else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'trade_count': self.trade_count
        }
    
    def to_admin_dict(self):
        """返回管理员查看的完整信息"""
        return {
            'id': self.id,
            'username': self.username,
            'device_id': self.device_id,
            'webhook_buy': self.webhook_buy,
            'webhook_buy_url': f'/api/webhook/{self.webhook_buy}',
            'webhook_sell': self.webhook_sell,
            'webhook_sell_url': f'/api/webhook/{self.webhook_sell}',
            'expire_date': self.expire_date.isoformat() if self.expire_date else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'trade_count': self.trade_count,
            'last_trade_at': self.last_trade_at.isoformat() if self.last_trade_at else None
        }

class TradeLog(db.Model):
    __tablename__ = 'trade_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trade_type = db.Column(db.String(10), nullable=False)  # buy or sell
    amount = db.Column(db.String(50), nullable=False)
    symbol = db.Column(db.String(20), default='BTCUSDT')
    status = db.Column(db.String(20), default='pending')  # pending, success, failed
    message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='trades')

class AdminUser(db.Model):
    """管理员账户"""
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_super_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)