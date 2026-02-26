# en2zh.py - Documentation Translator

A tool to automatically translate MicroPython/UIFlow2 documentation PO files from English to Chinese using OpenAI API, with support for batch processing and multi-threading.

## Prerequisites

### 1. Install Dependencies

Ensure you have the required Python packages installed. The tool requires `Babel`, `openai`, and `python-dotenv`.

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install Babel openai python-dotenv
```

### 2. Configure Environment Variables

Create a `.env` file in the root of the `docs` directory (or where you run the script from) to store your API credentials. **This prevents sensitive keys from being committed to the repository.**

**Example `.env` file content:**

```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=http://your-api-base-url/v1
OPENAI_MODEL=gpt-5.2
```

*   `OPENAI_API_KEY`: Your OpenAI API Key (Required).
*   `OPENAI_BASE_URL`: The API base URL (Optional, defaults to `http://192.168.20.176:3000/v1` if using a proxy or custom endpoint).
*   `OPENAI_MODEL`: The model to use (Optional, defaults to `gpt-5.2`).

## Usage

Run the script from the `docs` directory.

### 1. Translate All Files

To process all `.po` files under `docs/locales/zh_CN`:

```bash
python tools/en2zh.py
```

### 2. Translate a Single File

To translate a specific `.po` file:

```bash
python tools/en2zh.py locales/zh_CN/LC_MESSAGES/your_file.po
```

### 3. Adjust Concurrency (Multi-threading)

The tool uses multi-threading to speed up translation. The default worker count is **32**. You can adjust this using the `--workers` argument.

```bash
# Use 10 threads
python tools/en2zh.py --workers 10

# Use 50 threads for a specific file
python tools/en2zh.py locales/zh_CN/LC_MESSAGES/your_file.po --workers 50
```

## Features

*   **Prompt-Based Translation**: Loads system prompt/rules from `.github/prompts/en2zh.prompt.md`.
*   **Smart FilteringAnd Skipping**:
    *   Skips entries that already have a translation.
    *   Handles `Fuzzy` entries: Automatically removes the `fuzzy` flag and clears the old translation to force a re-translation.
    *   Skips placeholders (e.g., `|image.png|`) and file names.
    *   Uses a fixed translation dictionary (case-insensitive) for common terms.
    *   Ignores specific API terms like `Returns`, `Parameters`, etc.
*   **Babel Integration**: Uses `babel` library for robust PO file parsing and writing.
