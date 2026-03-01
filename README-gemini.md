# php-analysis（PHP 分支/巢狀複雜度分析器）- Gemini 版本

這個專案收錄了多個「以正規表示式/淺層字串解析」為主的 PHP 靜態掃描器，用來統計程式碼中的 `if / elseif / else` 分支數量、巢狀深度，並輸出 `analysis_report.json` 報表。

此 README 專注於 `gemini/` 目錄下的版本。

> **版本特色**：這是專案中一個較簡化的實作。它主要依賴計算大括號 `{}` 的方式來判斷巢狀深度，且未進行完整的原始碼「消毒」（例如移除註解、字串內容），因此在解析複雜或非標準格式的程式碼時，準確度可能較低。
>
> 優點：程式碼相對簡單，容易理解核心邏輯。

## 目錄結構

- `codex/`：較完整的版本，會先「消毒」原始碼，支援多元語法。
- `claude/`：功能較多、輸出選項較完整的版本。
- `gemini/`：**目前介紹的版本**，為較簡化的實作。

## 需求

- Python 3
- 無額外第三方依賴。

## 快速開始

在本 repo 根目錄下執行 `make` 指令：

```bash
make -C gemini run DIR=/path/to/your/php/project
```

或直接執行 Python 腳本：

```bash
python3 gemini/php_analyzer.py /path/to/your/php/project
```

執行完成後，會在「當前工作目錄」產生 `analysis_report.json`，並在終端機印出掃描摘要，包含：

- 掃描檔案總數
- 分支總數
- 複雜度（依最大深度）前 10 名的檔案
- 各檔案的分支數量統計

## 執行測試

若要驗證分析器的基本功能，可以執行單元測試：

```bash
make -C gemini test
```

## 輸出報表格式

`gemini` 版本的 `analysis_report.json` 結構如下：

```json
{
  "summary": {
    "total_files_scanned": 15,
    "total_files_with_branches": 10,
    "total_branches": 50,
    "most_complex_files": [
      {
        "file": "path/to/complex_file.php",
        "max_depth": 5,
        "total_branches": 12
      }
    ]
  },
  "files": {
    "path/to/file.php": {
      "max_depth": 3,
      "total_branches": 8,
      "branches": [
        {
          "type": "if",
          "line": 25,
          "depth": 1,
          "condition": "$user->isLoggedIn()"
        }
      ]
    }
  }
}
```
