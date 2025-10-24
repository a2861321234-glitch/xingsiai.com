# 形思工业设计网站

一个使用 Flask 构建的响应式企业官网，包含案例详情页、动态滚动动画以及可登录的内容管理后台。

## 功能概览

- 深色现代化 UI，包含首页、关于形思、设计案例、创新服务与联系我们分区。
- 至少 60 个案例，分为“外观设计”和“结构设计”两类，每个案例均有独立详情页展示 6 张 16:9 图片。
- 交互动画：滚动触发背景渐变、卡片淡入、悬停缩放等效果。
- 响应式导航：桌面端固定导航栏，移动端折叠式菜单。
- 后台管理系统：登录后可更新首页及联系方式文案，新增/编辑/删除案例并上传图片资源。

## 本地运行

1. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

2. 复制环境变量模板并修改默认账号信息：

   ```bash
   cp .env.example .env
   ```

3. 启动服务：

   ```bash
   flask --app app.py run
   ```

   或使用 Python：

   ```bash
   python app.py
   ```

4. 默认后台账号来自 `.env`：

   - 用户名：`ADMIN_USERNAME`
   - 密码：`ADMIN_PASSWORD`

   登录地址：`/admin/login`

## 内容管理

- 新增案例时需上传封面及 6 张 16:9 图片，未上传时系统会使用占位图。
- 编辑案例支持替换任意图片，系统自动保持 6 张图展示。
- “站点信息设置”页面可维护首页标题、副文案、CTA 按钮与联系信息等内容。

## 项目结构

```
app/
├── __init__.py          # Flask 工厂与初始化
├── admin_routes.py      # 后台相关路由
├── models.py            # SQLAlchemy 数据模型
├── routes.py            # 前台展示路由
├── static/
│   ├── css/style.css    # 全站样式
│   ├── img/placeholder-16x9.svg
│   └── js/main.js       # 动效与交互脚本
└── templates/
    ├── base.html
    ├── index.html
    ├── project_detail.html
    └── admin/...        # 后台模板
```

## 数据初始化

应用启动时会自动：

- 创建管理员账号（若不存在）。
- 初始化站点基础信息。
- 确保案例数量不少于 60 个（使用占位图片，可在后台逐步替换）。

## 部署建议

- 将 `DEBUG` 关闭并设置强随机 `FLASK_SECRET_KEY`。
- 使用 Nginx/Apache 反向代理至 WSGI 服务器（如 gunicorn 或 uWSGI）。
- 配置独立的静态资源存储与 CDN，以提升图片加载性能。
