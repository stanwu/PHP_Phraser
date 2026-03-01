# php-analysis（PHP 分支/巢狀複雜度分析器）

這個專案收錄了多個「以正規表示式/淺層字串解析」為主的 PHP 靜態掃描器，用來統計程式碼中的 `if / elseif / else` 分支數量、巢狀深度，並輸出 `analysis_report.json` 報表（方便找出條件分支最複雜的檔案/函式）。

> 特色：不需要安裝 PHP 或 AST 解析器；主要依賴 Python 標準函式庫。  
> 注意：這是 *best-effort* 的文字掃描器，遇到非常複雜的語法/字串拼接/不規則格式時可能會有誤判。

## 目錄結構

- `codex/`：較完整的版本
  - 會先「消毒」PHP 原始碼（把字串、註解、heredoc/nowdoc 內容換成空白但保留換行），降低誤判
  - 支援一般大括號語法與 alternative syntax：`if (...): ... endif;`
  - 會嘗試把分支歸類到函式（`function foo(...) { ... }`）底下
- `claude/`：功能較多、輸出選項較完整（可指定 `--output/--indent`），並附較完整測試
- `gemini/`：較簡化的版本（主要以大括號計算深度；不做完整的字串/註解消毒）

## 需求

- Python 3（建議 `>= 3.10` 以確保 `codex/` 版本可直接執行）
- 無額外第三方依賴（`claude/` 的 `make lint` 會用到 `ruff`，屬於可選）

## 快速開始（建議用 `codex/`）

在本 repo 內執行：

```bash
make -C codex analyze DIR=/path/to/your/php/project
```

或直接跑腳本：

```bash
python3 codex/php_analyzer.py /path/to/your/php/project
```

執行完成後會在「當前工作目錄」產生 `analysis_report.json`，並在終端機印出摘要（掃描檔案數、分支總數、複雜度前 10 名等）。

## 其他版本用法

### `claude/`

```bash
make -C claude run DIR=/path/to/your/php/project
# 或：
python3 claude/php_analyzer.py /path/to/your/php/project --output analysis_report.json --indent 2
```

### `gemini/`

```bash
make -C gemini run DIR=/path/to/your/php/project
# 或：
python3 gemini/php_analyzer.py /path/to/your/php/project
```

## 執行測試

```bash
make -C codex test
make -C claude test
make -C gemini test
```

## 輸出報表（概念）

每個實作的 JSON 結構略有不同，但核心都是：

- `summary`：整體統計（掃描檔案數、分支總數、最複雜檔案列表）
- `files`：逐檔案的分支資訊（分支型別、行號、深度、條件字串等）

如果你要把報表接到其他工具（例如 CI Gate、可視化儀表板），建議先選定要依賴哪個目錄的輸出格式（通常以 `codex/` 或 `claude/` 版本為主）。
