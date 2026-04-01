# 智记侠后端服务 (ZhiJiReminder Backend)

基于FastAPI的作业提醒系统后端，支持OCR识别、AI解析和任务管理。

## 功能特性

- 📷 **图片上传与OCR识别**：支持base64和文件上传
- 🤖 **AI智能解析**：使用大模型解析作业信息（课程、内容、截止时间）
- 📅 **任务管理**：创建、查询、完成、删除作业提醒
- ⏰ **时间计算**：自动计算剩余时间（天、小时、分钟）
- 👥 **用户管理**：用户信息存储与查询
- 🔄 **CORS支持**：跨域资源共享，支持小程序调用

## 本地开发

### 环境要求
- Python 3.8+
- pip

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动服务
```bash
# 方式1：使用启动脚本
python StartServer.py

# 方式2：直接启动
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 开发模式（热重载）
python StartServer.py --reload
```

### API文档
启动后访问：`http://localhost:8000/docs`

## Render部署

### 部署步骤

1. **推送代码到GitHub**
   ```bash
   git add .
   git commit -m "准备Render部署"
   git push origin main
   ```

2. **在Render创建Web Service**
   - 访问 [render.com](https://render.com)
   - 点击 "New +" → "Web Service"
   - 连接GitHub仓库：`tianqiyuan520/ZhiJiReminderBackend`
   - 使用以下配置：
     - **Name**: `zhijixiabackend`
     - **Region**: `Singapore (Southeast Asia)`
     - **Branch**: `main`
     - **Runtime**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     - **Plan**: `Free`

3. **环境变量（可选）**
   - `DB_PATH`: 数据库文件路径（默认：`zhi_ji_xia.db`）
   - `PORT`: 服务端口（Render自动设置）

4. **部署**
   - 点击 "Create Web Service"
   - Render会自动构建和部署

### 部署后测试

1. **检查健康状态**
   ```
   GET https://zhijixia-backend.onrender.com/
   ```
   应返回：`"智记侠API服务运行中"`

2. **测试API**
   ```
   GET https://zhijixia-backend.onrender.com/api/reminders?user_id=test_user_001
   ```

3. **查看API文档**
   ```
   https://zhijixia-backend.onrender.com/docs
   ```

## API接口

### 基础接口
- `GET /` - 健康检查
- `GET /docs` - API文档（Swagger UI）

### 图片处理
- `POST /api/upload` - 上传base64图片
- `POST /api/upload-file` - 上传图片文件

### 作业分析
- `POST /api/analyze` - 分析作业（拖延预测、微习惯拆解）

### 提醒管理
- `POST /api/reminder` - 创建提醒
- `GET /api/reminders` - 获取用户所有提醒
- `POST /api/reminders/{id}/complete` - 标记为已完成
- `DELETE /api/reminders/all` - 删除所有任务
- `DELETE /api/reminders/completed` - 删除已完成任务
- `DELETE /api/reminders/expired` - 删除已过期任务

### 用户管理
- `POST /api/user` - 保存用户信息
- `GET /api/user` - 获取用户信息

## 项目结构

```
ZhiJiReminder_Backend/
├── app/                    # 应用代码
│   ├── __init__.py
│   ├── main.py            # 主应用入口
│   ├── models.py          # Pydantic模型
│   ├── ocr.py             # OCR识别模块
│   └── llm.py             # 大模型解析模块
├── requirements.txt       # Python依赖
├── render.yaml           # Render部署配置
├── StartServer.py        # 本地启动脚本
├── README.md             # 项目说明
└── zhi_ji_xia.db         # SQLite数据库（本地）
```

## 前端配置

小程序前端需要更新API地址：

```javascript
// 在 utils/api.js 中
const baseUrl = 'https://zhijixia-backend.onrender.com'; // Render部署地址
// 或
const baseUrl = 'http://localhost:8000'; // 本地开发
```

## 注意事项

1. **免费计划限制**
   - Render免费实例在闲置时会休眠
   - 首次访问需要等待唤醒（约30-60秒）
   - 不支持持久化存储（数据库可能被重置）

2. **生产环境建议**
   - 升级到付费计划以获得更好性能
   - 使用外部数据库（如PostgreSQL）
   - 配置自定义域名和SSL证书
   - 设置环境变量保护敏感信息

3. **数据库持久化**
   - 免费计划不保证数据持久性
   - 考虑使用Render的PostgreSQL插件
   - 或定期备份数据库

## 故障排除

### 部署失败
- 检查 `requirements.txt` 依赖是否正确
- 查看Render构建日志
- 确保Python版本兼容（3.8+）

### 服务无法启动
- 检查端口配置（Render使用`$PORT`环境变量）
- 查看应用日志
- 验证数据库连接

### API调用失败
- 检查CORS配置
- 验证请求格式
- 查看服务日志

## 技术支持

如有问题，请：
1. 查看Render部署日志
2. 检查API文档 `/docs`
3. 查看应用日志输出

## 许可证

本项目仅供学习交流使用。
