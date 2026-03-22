# 🚀 超简单部署指南 - 只需3步

## 第一步：确认代码已在 GitHub ✅
打开 https://github.com/lvzengqin-cmd/ceyishijian-ai-backend
确认代码已上传（能看到 app.py、templates 等文件）

---

## 第二步：部署到 Render（2分钟）

### 1. 登录 Render
- 打开 https://render.com
- 点击右上角 "Get Started for Free"
- 选择 "Continue with GitHub"
- 授权登录

### 2. 创建服务
- 点击 "New +"（在页面右上角）
- 选择 "Web Service"
- 找到你的仓库 `ceyishijian-ai-backend`，点击 "Connect"

### 3. 配置服务（全部用默认）
- **Name**: 保持默认 `ceyishijian-ai-backend`
- **Runtime**: 保持默认 `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`

### 4. 添加环境变量（点击 "Advanced" 按钮）
点击 "Add Environment Variable" 添加以下3个：

| 名称 | 值 |
|------|-----|
| `SECRET_KEY` | `shijian-ai-secret-2024` |
| `ADMIN_USERNAME` | `admin` |
| `ADMIN_PASSWORD` | 你自己设一个密码 |

### 5. 创建
- 点击页面底部 "Create Web Service"
- 等待3-5分钟（可以看到部署日志）

---

## 第三步：获取地址给我

部署完成后，你会看到类似：
```
https://ceyishijian-ai-backend.onrender.com
```

**复制这个地址发给我**，我立即更新APP并构建APK！

---

## 📋 部署后测试

打开浏览器访问：
```
https://你的地址/admin
```

输入用户名 `admin` 和你设置的密码，应该能看到管理后台。

---

**有问题随时找我！**