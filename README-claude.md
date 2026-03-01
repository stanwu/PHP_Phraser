# php-analysis（PHP 分支/巢狀複雜度分析器）- Claude 版本

這個專案收錄了多個「以正規表示式/淺層字串解析」為主的 PHP 靜態掃描器，用來統計程式碼中的 `if / elseif / else` 分支數量、巢狀深度，並輸出 `analysis_report.json` 報表。

此 README 專注於 `claude/` 目錄下的版本。

> **版本特色**：這是專案中功能最完整的實作。
>
> - 掃描前先完整「消毒」原始碼（移除單行/多行註解、雙引號/單引號字串、heredoc/nowdoc），大幅降低誤判率
> - 深度計算採用 `max(brace_depth, indent_depth)`，兼顧大括號計數與縮排估算
> - 自動將分支歸類到所屬函式/方法；不屬於任何函式的分支歸入 `<global>` 虛擬項目
> - 提供 `--output` 與 `--indent` CLI 選項，方便整合進 CI 流程
> - 附完整單元測試（覆蓋 helper 函式與端對端的目錄掃描）

## 目錄結構

```
claude/
├── php_analyzer.py      # 主程式
├── Makefile             # 常用指令捷徑
└── tests/
    ├── __init__.py
    └── test_php_analyzer.py   # 單元測試
```

## 需求

- Python 3.8+
- 無額外第三方執行依賴
- （選用）`ruff`：`make lint` 時使用

## 快速開始

從本 repo 根目錄執行：

```bash
make -C claude run DIR=/path/to/your/php/project
```

或直接執行腳本：

```bash
python3 claude/php_analyzer.py /path/to/your/php/project
```

支援額外選項：

```bash
python3 claude/php_analyzer.py /path/to/your/php/project \
    --output my_report.json \
    --indent 4
```

| 選項 | 預設值 | 說明 |
|------|--------|------|
| `--output` / `-o` | `analysis_report.json` | JSON 報表輸出路徑 |
| `--indent` | `2` | JSON 縮排層數；設為 `0` 輸出緊湊格式 |

## 執行測試

```bash
make -C claude test
```

或不透過 make：

```bash
cd claude && python3 -m unittest -v
```

## 執行 Lint

需先安裝 `ruff`（`pip install ruff`）：

```bash
make -C claude lint
```

## 輸出報表格式

`analysis_report.json` 的結構如下：

```json
{
  "summary": {
    "total_files": 15,
    "total_branches": 87,
    "most_complex": [
      {
        "file": "src/Controller/OrderController.php",
        "max_depth": 6,
        "total_branches": 22
      }
    ]
  },
  "files": {
    "src/Controller/OrderController.php": {
      "max_depth": 6,
      "total_branches": 22,
      "branches": [
        {
          "type": "if",
          "line": 42,
          "depth": 2,
          "condition": "$order->getStatus() === ''"
        },
        {
          "type": "elseif",
          "line": 45,
          "depth": 2,
          "condition": "$order->getStatus() === ''"
        },
        {
          "type": "else",
          "line": 48,
          "depth": 2,
          "condition": ""
        }
      ],
      "functions": [
        {
          "name": "processOrder",
          "start_line": 38,
          "end_line": 65,
          "total_branches": 5,
          "max_depth": 3,
          "branches": [ "..." ]
        },
        {
          "name": "<global>",
          "start_line": 1,
          "end_line": 120,
          "total_branches": 2,
          "max_depth": 1,
          "branches": [ "..." ]
        }
      ]
    }
  }
}
```

> **注意**：字串內容在分析前已被替換為 `""` / `''`，因此 `condition` 欄位中的字串鍵值（如 `$item['type']`）會顯示為 `$item['']`，這是預期行為。

## 終端機摘要輸出範例

```
Scanning PHP files under: /path/to/your/php/project

============================================================
  PHP Branch Complexity Analysis
============================================================
  Total files scanned : 15
  Total branches found: 87

  Top 10 most complex files (by max nesting depth):
  --------------------------------------------------------
  File                                     MaxDepth Branches
  --------------------------------------------------------
  src/Controller/OrderController.php              6       22
  src/Service/PaymentService.php                  5       18
  ...
============================================================
```

## 與其他版本的比較

| 特性 | `claude/` | `codex/` | `gemini/` |
|------|:---------:|:--------:|:---------:|
| 字串/註解消毒 | ✓ | ✓ | ✗ |
| heredoc/nowdoc 處理 | ✓ | ✓ | ✗ |
| 深度計算方式 | brace + indent | brace + indent | 僅 brace |
| 函式分組 | ✓ | ✓ | ✗ |
| `--output` / `--indent` 選項 | ✓ | ✗ | ✗ |
| 單元測試 | ✓（獨立 tests/ 目錄） | ✓ | ✓ |
| ruff lint 支援 | ✓ | ✗ | ✗ |
