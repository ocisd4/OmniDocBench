# OmniDocBench 項目文檔索引

> **OmniDocBench** - 真實場景中多樣化文檔解析的綜合評估基準測試系統

這是 OmniDocBench 項目的主要文檔入口，為 AI 輔助開發和技術參考提供全面的技術文檔。

---

## 📋 項目概覽

### 基本資訊

- **項目類型**：數據處理與評估管道（Monolith 架構）
- **主要語言**：Python 3.x
- **倉庫**：https://github.com/opendatalab/OmniDocBench
- **論文**：[arXiv:2412.07626](https://arxiv.org/abs/2412.07626)
- **會議**：CVPR 2025
- **版本**：v1.5

### 核心能力

OmniDocBench 是一個專門設計用於評估文檔解析性能的基準測試系統：

- ✅ **1355 個 PDF 頁面**：涵蓋 9 種文檔類型、4 種版面類型、3 種語言
- ✅ **豐富的標註**：15 種塊級標註（20k+）+ 4 種跨度級標註（80k+）
- ✅ **多維度評估**：端到端、版面檢測、表格識別、公式識別、文字 OCR
- ✅ **靈活的框架**：配置驅動、模塊化、可擴展

### 快速參考

| 類別 | 技術 / 資訊 |
|------|-------------|
| **主要框架** | pandas, numpy, opencv-python, mmeval |
| **評估指標** | Edit Distance, TEDS, CDM, BLEU, METEOR, COCO mAP/mAR |
| **架構模式** | 註冊表模式 + 管道架構 |
| **配置方式** | YAML 配置文件 |
| **入口點** | 配置驅動評估（`configs/*.yaml`） |
| **結果輸出** | `result/` 目錄（JSON 格式） |

---

## 📚 生成的文檔

### 核心文檔

- **[項目概覽](./project-overview.md)** 📖
  - 執行摘要和項目分類
  - 技術棧詳解
  - 評估類別和支持的指標
  - 數據集特點和關鍵特性

- **[原始碼樹狀結構分析](./source-tree-analysis.md)** 🌳
  - 完整目錄樹結構
  - 關鍵目錄詳解
  - 入口點和模塊初始化
  - 代碼組織模式

- **[架構文檔](./architecture.md)** 🏗️
  - 架構模式深度分析
  - 技術棧和依賴關係
  - 核心算法實現
  - API 設計和組件交互
  - 數據架構和數據流

- **[開發指南](./development-guide.md)** 🔧
  - 環境設置和安裝
  - 基本使用和評估流程
  - 添加新組件（指標、任務、數據集）
  - 測試和故障排除
  - 性能優化和開發工作流程

- **[OCR 多模型比較評估指南](./ocr-comparison-eval-guide.md)** 📊
  - 系統架構與元件關係圖
  - 配置說明與參數詳解
  - 執行流程與序列圖
  - 輸出報告格式解析（Markdown、JSON、錯誤分析）
  - 指標說明（Edit_dist 子指標、TEDS）
  - 使用範例與擴展指南

---

## 📂 現有項目文檔

### 官方文檔

- **[README（英文）](../README.md)** - 主要項目文檔
- **[README（簡體中文）](../README_zh-CN.md)** - 中文項目文檔
- **[貢獻者許可協議](../OmniDocBench_CLA.md)** - CLA 說明
- **[LICENSE](../LICENSE)** - MIT 許可證

### 模塊文檔

- **[CDM 指標文檔（英文）](../metrics/cdm/README.md)** - CDM 評估指標說明
- **[CDM 指標文檔（中文）](../metrics/cdm/README-CN.md)** - CDM 中文文檔

---

## 🚀 快速開始

### 1. 安裝

#### 方法 A：使用 uv（推薦，速度更快）

```bash
# 安裝 uv（如果尚未安裝）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆倉庫
git clone https://github.com/opendatalab/OmniDocBench.git
cd OmniDocBench

# 創建虛擬環境並安裝依賴
uv venv .venv
source .venv/bin/activate  # Linux/macOS
uv pip install -r requirements.txt
```

#### 方法 B：使用 pip

```bash
# 克隆倉庫
git clone https://github.com/opendatalab/OmniDocBench.git
cd OmniDocBench

# 創建虛擬環境（推薦）
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# 安裝依賴
pip install -r requirements.txt
```

### 2. 下載數據集

- **Hugging Face**：https://huggingface.co/datasets/opendatalab/OmniDocBench
- **OpenDataLab**：https://opendatalab.com/OpenDataLab/OmniDocBench

### 3. 運行評估

```bash
# 端到端評估
python run_eval.py --config configs/end2end.yaml

# 版面檢測
python run_eval.py --config configs/layout_detection.yaml

# 公式識別
python run_eval.py --config configs/formula_recognition.yaml

# 表格識別
python run_eval.py --config configs/table_recognition.yaml
```

### 4. 查看結果

```bash
# 結果保存在 result/ 目錄
ls result/

# 查看彙總結果
cat result/end2end_quick_match_metric_result.json | jq .
```

---

## 🎯 主要評估任務

### 1. 端到端評估（End-to-End）

**配置**：`configs/end2end.yaml`

評估完整的文檔解析流程，包括：
- 文本塊識別和 OCR
- 公式識別
- 表格識別
- 閱讀順序

**支持的指標**：Edit Distance, BLEU, METEOR, TEDS, CDM

### 2. 版面檢測（Layout Detection）

**配置**：`configs/layout_detection.yaml`

評估文檔版面元素的檢測性能。

**支持的指標**：COCO mAP, mAR

### 3. 公式識別（Formula Recognition）

**配置**：`configs/formula_recognition.yaml`

評估數學公式的識別準確性。

**支持的指標**：Edit Distance, CDM

### 4. 表格識別（Table Recognition）

**配置**：`configs/table_recognition.yaml`

評估表格結構和內容的識別。

**支持的指標**：TEDS, Edit Distance

### 5. 文字 OCR

**配置**：`configs/ocr.yaml`

評估文字識別準確性。

**支持的指標**：Edit Distance, BLEU, METEOR

### 6. OCR 多模型比較評估

**配置**：`configs/ocr_comparison.yaml`

同時評估多個 OCR 模型，生成比較報告。

**主要功能**：
- 多模型同時評估
- 按文件來源分類統計（paper、presentation、handwriting 等）
- 自動生成 Markdown、JSON 及錯誤分析報告

**支持的指標**：Edit Distance（含子指標）、TEDS

**詳細文檔**：[OCR 多模型比較評估指南](./ocr-comparison-eval-guide.md)

---

## 🏛️ 架構亮點

### 註冊表模式（Registry Pattern）

動態組件管理系統：

```python
# 註冊評估任務
@EVAL_TASK_REGISTRY.register("end2end_eval")
class End2EndEval:
    pass

# 註冊評估指標
@METRIC_REGISTRY.register("TEDS")
class call_TEDS:
    pass

# 註冊數據集
@DATASET_REGISTRY.register("end2end_dataset")
class End2EndDataset:
    pass
```

### 配置驅動設計

通過 YAML 文件定義評估流程：

```yaml
end2end_eval:
  metrics:
    text_block:
      metric: [Edit_dist]
    display_formula:
      metric: [Edit_dist, CDM_plain]
    table:
      metric: [TEDS, Edit_dist]
  dataset:
    dataset_name: end2end_dataset
    ground_truth:
      data_path: ./demo_data/omnidocbench_demo/OmniDocBench_demo.json
    prediction:
      data_path: ./demo_data/end2end
    match_method: quick_match
```

### 模塊化架構

```
配置層 (configs/)
    ↓
任務層 (task/)
    ↓
數據層 (dataset/) + 指標層 (metrics/)
    ↓
工具層 (utils/)
    ↓
註冊表層 (registry/)
```

---

## 🛠️ 開發指引

### 添加新的評估指標

1. 在 `metrics/` 中創建指標類
2. 使用 `@METRIC_REGISTRY.register()` 註冊
3. 實現 `evaluate()` 方法
4. 在配置文件中引用

詳見：[開發指南 - 添加新的評估指標](./development-guide.md#添加新的評估指標)

### 添加新的評估任務

1. 在 `task/` 中創建任務類
2. 使用 `@EVAL_TASK_REGISTRY.register()` 註冊
3. 協調數據加載和指標計算
4. 創建對應的配置文件

詳見：[開發指南 - 添加新的評估任務](./development-guide.md#添加新的評估任務)

### 添加新的數據集加載器

1. 在 `dataset/` 中創建數據集類
2. 使用 `@DATASET_REGISTRY.register()` 註冊
3. 實現數據加載和匹配邏輯
4. 在配置文件中指定數據集名稱

詳見：[開發指南 - 添加新的數據集加載器](./development-guide.md#添加新的數據集加載器)

---

## 📊 評估指標說明

### Edit Distance（編輯距離）

標準化的 Levenshtein 距離，測量兩個字符串之間的差異。

### TEDS（樹編輯距離相似度）

專門用於表格評估的指標，基於 HTML 樹結構的編輯距離。

### CDM（字符檢測指標）

用於公式評估的視覺匹配指標：
1. 將 LaTeX 渲染為圖像
2. 提取字符級邊界框
3. 計算視覺匹配準確率

詳見：[CDM 文檔](../metrics/cdm/README.md)

### BLEU / METEOR

NLP 評估指標，用於文本質量評估。

### COCO mAP / mAR

目標檢測標準指標，用於版面檢測評估。

---

## 🌐 外部資源

### 數據集

- [Hugging Face 數據集](https://huggingface.co/datasets/opendatalab/OmniDocBench)
- [OpenDataLab 數據集](https://opendatalab.com/OpenDataLab/OmniDocBench)

### 研究論文

- [arXiv 論文](https://arxiv.org/abs/2412.07626)

### 代碼倉庫

- [GitHub 倉庫](https://github.com/opendatalab/OmniDocBench)
- [Issues](https://github.com/opendatalab/OmniDocBench/issues)
- [Discussions](https://github.com/opendatalab/OmniDocBench/discussions)

---

## 🗂️ 目錄結構速查

```
OmniDocBench/
├── configs/          # 評估配置文件（YAML）
├── dataset/          # 數據集加載器
├── metrics/          # 評估指標實現
│   └── cdm/          # CDM 指標模塊
├── task/             # 評估任務定義
├── utils/            # 工具函數和匹配算法
├── demo_data/        # 演示數據
├── result/           # 評估結果輸出
├── tools/            # 推理工具
├── registry/         # 註冊表系統
└── docs/             # 項目文檔（本目錄）
```

---

## 💡 AI 輔助開發提示

### 使用此文檔進行 AI 開發

當使用 AI 輔助工具（如 Claude, ChatGPT, Copilot）開發 OmniDocBench 時：

1. **參考架構文檔**以了解設計模式和組件交互
2. **查閱開發指南**以獲取添加新組件的步驟
3. **使用原始碼樹分析**以快速定位相關代碼
4. **檢查項目概覽**以理解整體能力和限制

### 常見開發場景

- **添加新指標**：→ 架構文檔 + 開發指南
- **理解數據流**：→ 架構文檔（數據架構部分）
- **定位特定功能**：→ 原始碼樹分析
- **環境設置問題**：→ 開發指南（故障排除部分）

---

## 🔄 版本資訊

**當前版本**：v1.5

**主要更新**：
- ✅ 更新混合匹配算法（公式與文本可相互匹配）
- ✅ CDM 整合到指標模塊
- ✅ 圖像解析度提升（報紙/筆記：72 DPI → 200 DPI）
- ✅ 新增 374 頁數據
- ✅ 平衡中英文頁面比例
- ✅ 更新評分計算公式

**版本分支**：
- `main` - v1.5（當前）
- `v1_0` - v1.0

---

## 📞 獲取幫助

### 問題和錯誤報告

- **GitHub Issues**：https://github.com/opendatalab/OmniDocBench/issues

### 討論和問題

- **GitHub Discussions**：https://github.com/opendatalab/OmniDocBench/discussions

### 文檔導航

如果您不確定從哪裡開始：

- **初次使用**：→ [README](../README.md) → [開發指南](./development-guide.md)
- **理解架構**：→ [架構文檔](./architecture.md)
- **添加功能**：→ [開發指南](./development-guide.md#添加新組件)
- **查找代碼**：→ [原始碼樹分析](./source-tree-analysis.md)

---

## 🎉 貢獻

我們歡迎貢獻！請參閱：

- [貢獻者許可協議（CLA）](../OmniDocBench_CLA.md)
- [開發指南 - 貢獻部分](./development-guide.md#貢獻)

---

## 📜 許可證

本項目採用 **MIT 許可證**。詳見 [LICENSE](../LICENSE) 文件。

---

## 🤝 致謝

感謝所有為 OmniDocBench 做出貢獻的研究人員和開發者。

---

*本文檔由 BMM document-project workflow 自動生成*
*生成日期：2025-11-11*
*最後更新：2025-01-27（新增 OCR 多模型比較評估指南）*
*掃描模式：深度掃描*
*項目類型：數據處理管道*

**下次更新建議**：運行 `/bmad:bmm:workflows:document-project` 重新掃描項目以更新此文檔。
