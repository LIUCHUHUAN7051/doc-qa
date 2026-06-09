# 📄 文档问答 RAG 系统

上传 PDF / Word / TXT 文档，基于 AI 进行智能问答。

## 功能

- 支持多文件上传（PDF / Word / TXT）
- 基于 TF-IDF 的文档检索 + DeepSeek AI 问答
- 对话记录导出
- 美观的现代化界面

## 技术栈

- **前端/后端框架**: Streamlit
- **AI 模型**: DeepSeek API
- **检索引擎**: TF-IDF (scikit-learn)
- **文档解析**: pypdf, python-docx

## 本地运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

在侧边栏上传文档后即可开始提问。
