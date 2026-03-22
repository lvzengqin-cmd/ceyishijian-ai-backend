# 部署指南 - 事件AI量化管理后台

## 📋 项目说明

这是一个基于 Flask + SQLite 的管理后台系统，用于管理用户和 Webhook 链接。

**核心功能：**
1. ✅ 用户注册/登录
2. ✅ 自动生成 Webhook ID（用户不可见）
3. ✅ 后台管理面板
4. ✅ 查看用户列表和 Webhook 链接
5. ✅ 延长会员期限

---

## 🚀 免费部署方案（推荐：Render.com）

Render.com 提供免费托管服务，适合测试使用。

### 步骤1：注册 Render 账号
1. 访问 https://render.com
2. 使用 GitHub 账号登录

### 步骤2：创建 GitHub 仓库
1. 在 GitHub 创建新仓库（如 `shijian-ai-backend`）
2. 将本项目的所有文件推送上去

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/你的用户名/shijian-ai-backend.git
git push -u origin main
```

### 步骤3：在 Render 部署
1. 登录 Render 后，点击 "New +" → "Web Service"
2. 选择你的 GitHub 仓库
3. 配置如下：
   - **Name**: `shijian-ai-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
4. 点击 "Advanced" 设置环境变量：
   - `SECRET_KEY`: 随机字符串（如 `your-secret-key-12345`）
   - `ADMIN_USERNAME`: `admin`（管理员账号）
   - `ADMIN_PASSWORD`: `你的密码`（管理员密码）
5. 点击 "Create Web Service"

### 步骤4：访问管理后台
部署完成后，你会得到一个类似 `https://shijian-ai-backend.onrender.com` 的网址。

打开网址，使用你设置的账号密码登录即可。

---

## 🛠️ APP端配置修改

为了让 APP 连接到新后端，需要修改 Android 项目的配置。

### 1. 修改 Config.kt

打开 `/app/src/main/java/com/shijian/aitrading/utils/Config.kt`，修改 BASE_URL：

```kotlin
object Config {
    // 后端 API 地址（替换成你的 Render 地址）
    const val BASE_URL = "https://shijian-ai-backend.onrender.com"
    
    // 其他配置保持不变...
}
```

### 2. 移除 APP 中的 Webhook 显示

**SettingsActivity.kt** - 移除 Webhook 显示区域：

```kotlin
// 注释掉或删除 Webhook 相关代码
// rowWebhookBuy.visibility = View.GONE
// rowWebhookSell.visibility = View.GONE
```

**activity_settings.xml** - 隐藏 Webhook 部分：

```xml
<!-- Webhook 配置 -->
<LinearLayout
    android:id="@+id/section_webhook"
    android:visibility="gone">  <!-- 添加这行 -->
    ...
</LinearLayout>
```

### 3. 重新构建 APK

```bash
./gradlew assembleDebug
```

---

## 📱 完整使用流程

### 用户端流程：
1. 用户下载 APP
2. 用户注册（提交用户名、密码、设备ID）
3. 系统自动在后端创建账号，生成 Webhook ID
4. APP 显示"系统已配置完成"（不显示 Webhook 链接）
5. 用户完成交易APP配置
6. 用户开启自动交易，等待信号

### 管理员端流程：
1. 打开管理后台网址
2. 登录管理员账号
3. 在"用户管理"查看所有注册用户
4. 点击用户查看详情
5. 复制该用户的 Webhook 链接（做多/做空）
6. 将 Webhook 配置到你的飞书/其他信号平台
7. 当信号触发时，自动推送到用户手机执行交易

---

## 🔧 管理后台功能说明

### 控制台
- 查看总用户数、活跃用户、过期用户、今日交易数
- 查看最近注册用户
- 查看最近交易记录

### 用户管理
- 查看所有用户列表
- 显示设备ID（点击复制）
- 显示会员状态
- 点击"详情"进入用户详情页

### 用户详情页
- 查看完整用户信息
- **Webhook 链接（重要！）**：
  - 显示做多 Webhook URL
  - 显示做空 Webhook URL
  - 一键复制按钮
- 会员管理：延长会员期限（7天/30天/90天/1年）
- 交易记录：查看该用户的所有交易历史

---

## 💡 商业模式说明

通过这种方式：
1. **用户无法绕过平台** - 他们不知道自己的 Webhook 链接
2. **你控制信号源** - 只有你知道 Webhook 链接，可以在后台配置
3. **灵活的会员管理** - 可以随时延长或缩短用户会员期限
4. **数据掌控** - 所有用户数据和交易记录都在你手中

---

## ⚠️ 注意事项

1. **Render 免费版限制**：
   - 30分钟无访问会自动休眠
   - 首次访问需要等待几秒唤醒
   - 每月 750 小时免费（足够使用）

2. **数据持久化**：
   - 使用 SQLite 数据库
   - 数据保存在 Render 的磁盘上
   - 除非手动删除，否则数据不会丢失

3. **安全性**：
   - 管理员密码请设置复杂一些
   - SECRET_KEY 请使用随机字符串
   - 建议后续升级到 PostgreSQL + Redis

---

## 📝 API 文档

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

### 接收信号（Webhook）
```
POST /api/webhook/{webhook_id}
Content-Type: application/json

{
    "type": "buy",
    "amount": "100",
    "symbol": "BTCUSDT"
}
```

---

有问题随时问我！
