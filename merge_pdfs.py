"""合并两个 PDF 文件为一个 PDF"""
import sys
from pathlib import Path

try:
    from pypdf import PdfWriter
except ImportError:
    print("请先安装 pypdf: pip install pypdf")
    sys.exit(1)


def merge_pdfs(pdf_list: list[str], output: str):
    writer = PdfWriter()
    for pdf in pdf_list:
        writer.append(pdf)
        print(f"  + {Path(pdf).name}")
    writer.write(output)
    writer.close()
    print(f"\n✅ 已合并到: {output}")


if __name__ == "__main__":
    # 改这里的路径就行
    files = [
        r"D:\WeChat\聊天记录\xwechat_files\wxid_cg7f9w2l7byh22_a155\msg\file\2026-04\刘理鑫2405321138.pdf",
        r"C:\Users\LIUCHUHUAN\刘理鑫_AI应用开发求职信.pdf",
    ]
    output = r"C:\Users\LIUCHUHUAN\刘理鑫_简历+求职信.pdf"
    merge_pdfs(files, output)
