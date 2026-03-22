# 后端部署步骤

## 1. 推送代码到 GitHub

在你的服务器/电脑上执行：

```bash
# 克隆你的空仓库
git clone https://github.com/lvzengqin-cmd/ceyishijian-ai-backend.git
cd ceyishijian-ai-backend

# 复制后端代码文件
# 把所有文件从 /root/.openclaw/workspace/shijian-ai-backend/ 复制到这里

# 提交并推送
git add .
git commit -m "Initial commit"
git push origin main
```

## 2. 部署到 Render.com

1. 访问 https://render.com
2. 用 GitHub 登录
3. 点击 "New +" → "Web Service"
4. 选择你的仓库 `ceyishijian-ai-backend`
5. 配置：
   - **Name**: `ceyishijian-ai-backend`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
6. 点击 "Advanced" 添加环境变量：
   - `SECRET_KEY`: 任意随机字符串（如 `your-secret-key-123456`）
   - `ADMIN_USERNAME`: `admin`
   - `ADMIN_PASSWORD`: 你的管理员密码
7. 点击 "Create Web Service"

## 3. 获取部署地址

部署完成后，你会得到一个类似：
`https://ceyishijian-ai-backend.onrender.com`

把这个地址发给我，我更新 APP 配置。

## 4. 管理后台登录

打开 `https://你的地址/admin`
使用你设置的用户名密码登录。

---

**或者直接下载代码 zip 包：**
所有代码在 `/root/.openclaw/workspace/shijian-ai-backend/`
你可以直接下载这个文件夹打包上传。