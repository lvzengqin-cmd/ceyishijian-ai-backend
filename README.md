# 事件AI量化 - 管理后台

## 项目结构
```
shijian-ai-backend/
├── app.py              # Flask主程序
├── models.py           # 数据库模型
├── requirements.txt    # Python依赖
├── render.yaml         # Render部署配置
├── templates/          # HTML模板
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   └── users.html
└── static/             # 静态文件
    └── css/
        └── style.css
```

## 功能
1. 用户注册/登录
2. 设备ID绑定
3. Webhook自动生成
4. 后台管理面板
5. 用户列表查看

## 部署

### 本地测试
```bash
pip install -r requirements.txt
python app.py
```

### 部署到 Render（免费）
1. 推送代码到 GitHub
2. 在 Render.com 创建 Web Service
3. 选择 Python 环境
4. 设置环境变量：
   - `SECRET_KEY` = 随机字符串
   - `ADMIN_USERNAME` = 管理员账号
   - `ADMIN_PASSWORD` = 管理员密码

## API接口

### 用户注册
```
POST /api/register
Content-Type: application/json

{
    "username": "用户名",
    "password": "密码",
    "device_id": "设备ID"
}
```

### 用户登录
```
POST /api/login
Content-Type: application/json

{
    "username": "用户名",
    "password": "密码",
    "device_id": "设备ID"
}
```

### 获取用户信息
```
GET /api/user/info
Authorization: Bearer <token>
```

### 接收交易信号
```
POST /api/webhook/:webhook_id
Content-Type: application/json

{
    "type": "buy|sell",
    "amount": "100",
    "symbol": "BTCUSDT"
}
```
