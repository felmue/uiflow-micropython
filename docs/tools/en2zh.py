# SPDX-FileCopyrightText: 2026 M5Stack Technology CO LTD
#
# SPDX-License-Identifier: MIT

import concurrent.futures
from pathlib import Path
import openai
from babel.messages.pofile import read_po, write_po
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


def load_system_prompt() -> str:
    """Load translation rules from .github/prompts/en2zh.prompt.md, taking only the content after YAML front matter."""
    try:
        # Assuming en2zh.py is in docs/tools/, prompt is in .github/prompts/
        prompt_path = Path(__file__).resolve().parents[2] / ".github" / "prompts" / "en2zh.prompt.md"
        text = prompt_path.read_text(encoding="utf-8")

        lines = text.splitlines()
        if lines and lines[0].strip() == "---":
            # Skip YAML front matter
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    return "\n".join(lines[i + 1 :]).strip()
        return text.strip()
    except Exception as e:
        print(f"Warning: Failed to load system prompt from file: {e}")
        return "你是一位专业的翻译官。请将用户输入的英文内容翻译成中文。要求：译文自然、通顺，保留原意，不要多余的解释。"

SYSTEM_PROMPT = load_system_prompt()

def translate_en_to_zh(text):
    client = openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),  # 建议使用环境变量
        base_url=os.getenv("OPENAI_BASE_URL") # 如果使用代理，请修改此处
    )

    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL"),  # 或者使用 "gpt-4o", "gpt-3.5-turbo"
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.3, # 较低的温度值使输出更稳定、准确
        )

        # 提取翻译结果
        # print(response)
        return response.choices[0].message.content
    except Exception as e:
        print(f"发生错误: {e}")
        return ""

# 固定翻译
fixed_translation = {
    "UiFlow2 Example": "UiFlow2 应用示例",
    "MicroPython Example": "MicroPython 应用示例",
    "UiFlow2 Code Block:": "UiFlow2 代码块：",
    "MicroPython Code Block:": "MicroPython 代码块：",
    "Example output:": "示例输出：",
    "API": "API参考",
    "**API**": "API参考",
}

# 构建一个 key 全部小写的映射，便于大小写不敏感匹配
fixed_translation_ci = {k.lower(): v for k, v in fixed_translation.items()}

# 忽略翻译的条目（大小写敏感）
ignore_list = (
    "Returns",
    "Parameters",
    "Return type",
    "None",
    "Bases:"
)


def translate_message(message):
    """
    Worker function to translate a single message object.
    Returns the message object with updated translation if successful.
    """
    try:
        translated = translate_en_to_zh(message.id)
        if translated:
            message.string = translated
            return message
        else:
            print(f"Empty translation for {message.id}")
            return None
    except Exception as e:
        print(f"Error translating {message.id}: {e}")
        return None


def process_po_file(input_file, workers=10):
    # 1. 加载 PO 文件
    with open(input_file, 'rb') as f:
        catalog = read_po(f)

    print(f"成功加载文件: {input_file}")
    print(f"总条目数: {len(catalog)}")
    print("-" * 30)

    # 收集需要翻译的消息
    messages_to_translate = []

    # 2. 遍历所有条目,进行预处理和筛选
    for message in catalog:
        if not message.id:
            print("跳过头部条目")
            continue

        print(f"正在处理 msgid: {message.id}")

        # 处理 'Fuzzy' (模糊) 标记：对非头部条目，去掉 fuzzy 并清空译文
        if message.string and 'fuzzy' in message.flags:
            message.flags.remove('fuzzy')
            message.string = ""

        if message.string:
            print("已存在译文，跳过翻译")
            continue

        # 处理固定翻译的条目（忽略大小写）
        msgid_lower = message.id.lower() if message.id else ""
        if msgid_lower in fixed_translation_ci:
            message.string = fixed_translation_ci[msgid_lower]
            print(f"使用固定翻译: {message.string}")
            continue

        # 不处理占位符和图片文件名
        if (message.id.startswith("|") and message.id.endswith("|")) or message.id.endswith((".png", ".jpg", ".jpeg", ".gif", ".m5f2", ".py", ".svg", ".JPEG")):
            print(f"跳过翻译 (占位符或图片文件名): {message.id}")
            continue

        # 忽略特定条目
        if message.id in ignore_list:
            print(f"跳过翻译 (在忽略列表中): {message.id}")
            continue

        # 加入待翻译列表
        messages_to_translate.append(message)

    print(f"待翻译条目数: {len(messages_to_translate)}")

    # 3. 多线程翻译
    if messages_to_translate:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            # 提交所有翻译任务
            future_to_message = {executor.submit(translate_message, msg): msg for msg in messages_to_translate}

            # 获取结果
            completed_count = 0
            total_count = len(messages_to_translate)

            for future in concurrent.futures.as_completed(future_to_message):
                msg = future_to_message[future]
                try:
                    result = future.result()
                    completed_count += 1
                    # result 就是 msg 本身（如果成功）或 None
                    if result:
                        print(result.string)
                        # print(f"[{completed_count}/{total_count}] 翻译完成: {result.string[:50]}...")
                except Exception as exc:
                    print(f"Translation generated an exception: {exc}")

    print("-" * 30)

    # 4. 保存文件
    with open(input_file, 'wb') as f:
        write_po(f, catalog)
    print(f"文件已保存至: {input_file}")


# 测试翻译
if __name__ == "__main__":
    import argparse
    from dotenv import load_dotenv
    
    # 显式加载 .env 文件，如果存在
    load_dotenv()

    parser = argparse.ArgumentParser(description="Translate PO files.")
    parser.add_argument(
        "path",
        nargs="?",
        help="Path to a specific .po file or a directory containing .po files",
    )
    parser.add_argument("--workers", type=int, default=4, help="Number of worker threads")
    args, unknown = parser.parse_known_args() # handle other args potentially passed

    # 如果提供了路径参数，则处理指定文件或目录
    if args.path:
        target_path = Path(args.path)

        if target_path.is_file():
            print("=" * 60)
            print(f"开始处理单个文件: {target_path}")
            process_po_file(str(target_path), workers=args.workers)
            raise SystemExit(0)

        if target_path.is_dir():
            po_files = sorted(target_path.rglob("*.po"))
            if not po_files:
                print(f"在目录中未找到 .po 文件: {target_path}")
                raise SystemExit(1)

            print(f"在 {target_path} 下找到 {len(po_files)} 个 .po 文件")
            for po_path in po_files:
                print("=" * 60)
                print(f"开始处理: {po_path}")
                process_po_file(str(po_path), workers=args.workers)
            raise SystemExit(0)

        print(f"Path not found: {target_path}")
        raise SystemExit(1)

    # 遍历 docs/locales/zh_CN 下所有 .po 文件并处理
    docs_root = Path(__file__).resolve().parents[1]

    zh_cn_dir = docs_root / "locales" / "zh_CN"

    if not zh_cn_dir.is_dir():
        raise SystemExit(f"目录不存在: {zh_cn_dir}")

    po_files = sorted(zh_cn_dir.rglob("*.po"))
    print(f"在 {zh_cn_dir} 下找到 {len(po_files)} 个 .po 文件")

    for po_path in po_files:
        print("=" * 60)
        print(f"开始处理: {po_path}")
        process_po_file(str(po_path), workers=args.workers)
