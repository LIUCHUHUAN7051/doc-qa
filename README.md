<div align="center">
  <br>
  <h1>📄 文档问答 RAG 系统</h1>
  <p><strong>上传文档，AI 智能问答 — 支持 PDF / Word / TXT</strong></p>
  <br>
</div>

## ✨ 功能

| 功能 | 说明 |
|------|------|
| 📁 多文件上传 | 同时上传多个 PDF / Word / TXT，统一检索 |
| 🤖 AI 问答 | 基于文档内容回答问题，支持上下文对话 |
| 🔍 智能检索 | TF-IDF + 字符级 n-gram，精准定位相关内容 |
| 💾 导出对话 | 一键导出问答记录为 Markdown 文件 |
| 🎨 精致 UI | 渐变主题、平滑动效、响应式布局 |

## 🛠️ 技术栈

```
前端/后端框架  ─  Streamlit
AI 模型        ─  DeepSeek API
检索引擎       ─  TF-IDF (scikit-learn)
文档解析       ─  pypdf, python-docx
```

## 🚀 本地运行

```bash
# 1. 克隆仓库
git clone https://github.com/LIUCHUHUAN7051/doc-qa.git
cd doc-qa

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 API Key
# 在项目目录下创建 .env 文件，写入：
# DEEPSEEK_API_KEY=你的key

# 4. 启动
streamlit run app.py
```

打开浏览器访问 `http://localhost:8501`，在左侧上传文档即可开始提问。

## 📖 使用指南

1. **上传文档** — 点击左侧"上传文档"区域，选择 PDF / Word / TXT 文件（可多选）
2. **等待处理** — 系统自动解析文本并建立索引
3. **开始提问** — 在输入框中输入问题，AI 将根据文档内容回答
4. **导出记录** — 点击左侧"导出对话记录"保存问答内容

> 💡 第一次使用时需要准备 DeepSeek API Key，可在 [platform.deepseek.com](https://platform.deepseek.com) 获取。

## 📸 预览

<div align="center">
  <p><em>（此处可放一张运行截图）</em></p>
</div>

## 📂 项目结构

```
doc-qa/
├── app.py              # 主程序
├── requirements.txt    # 依赖清单
├── .env                # API Key 配置（不上传）
├── .gitignore          # Git 忽略规则
└── README.md           # 项目说明
```

## 👤 关于

- 作者：刘理鑫
- 求职方向：AI 应用开发工程师
- 邮箱：CHUIZI705179074@outlook.com
