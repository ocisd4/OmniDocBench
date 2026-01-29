"""
OCR 評估報告生成器

此模組提供 Markdown 和 JSON 報告生成功能，用於多模型 OCR 評估結果的比較報告。
報告內容根據配置中的 metrics 設定動態生成。
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


class OCRReportGenerator:
    """
    OCR 評估報告生成器

    根據評估結果生成 Markdown 和 JSON 格式的比較報告。
    報告內容由配置中的 metrics 設定動態決定。
    """

    # data_source 分類順序
    CATEGORY_ORDER = [
        "paper",
        "presentation",
        "handwriting",
        "receipt",
        "eBook",
        "finance",
        "form",
    ]

    # data_source 中英文名稱對照
    CATEGORY_NAMES = {
        "paper": "學術論文",
        "presentation": "簡報投影片",
        "handwriting": "手寫文件",
        "receipt": "收據發票",
        "eBook": "電子書",
        "finance": "財務報表",
        "form": "表格表單",
    }

    # 指標說明
    METRIC_DESCRIPTIONS = {
        "Edit_dist": "歸一化編輯距離 (0-1)，越低越好",
        "Edit_dist_ALL_page_avg": "頁面層級平均編輯距離",
        "Edit_dist_edit_whole": "整體編輯距離（所有字元合併計算）",
        "Edit_dist_edit_sample_avg": "樣本層級平均編輯距離",
        "TEDS": "表格結構編輯距離相似度 (0-1)，越高越好",
        "TEDS_structure_only": "表格結構相似度（僅結構）(0-1)，越高越好",
        "CDM": "公式字元偵測匹配分數 (0-1)，越高越好",
        "BLEU": "BLEU 分數 (0-1)，越高越好",
        "METEOR": "METEOR 分數 (0-1)，越高越好",
    }

    # Edit_dist 子指標列表
    EDIT_DIST_SUB_METRICS = ["ALL_page_avg", "edit_whole", "edit_sample_avg"]

    def __init__(
        self,
        results: dict[str, dict[str, Any]],
        metrics_config: dict[str, dict],
        gt_statistics: dict | None = None,
        errors_data: dict[str, dict] | None = None,
    ):
        """
        初始化報告生成器

        Args:
            results: 多模型評估結果，格式為：
                {
                    "ModelName": {
                        "elements": {
                            "text_block": {
                                "sample_count": N,
                                "all": {...},
                                "group": {...},
                                "page": {...}
                            }
                        }
                    }
                }
            metrics_config: 指標配置，格式與 YAML 中的 metrics 區塊相同
            gt_statistics: Ground Truth 統計資訊（總頁數、各元素類型數量）
            errors_data: 各模型的錯誤資訊，按元素類型和 data_source 分組
        """
        self.results = results
        self.metrics_config = metrics_config
        self.gt_statistics = gt_statistics or {}
        self.errors_data = errors_data or {}
        self.models = list(results.keys())
        self.generated_at = datetime.now()

    def _get_sorted_categories(self, categories: set[str]) -> list[str]:
        """根據預設順序排序分類"""
        sorted_cats = []
        for cat in self.CATEGORY_ORDER:
            if cat in categories:
                sorted_cats.append(cat)
        # 加入不在預設順序中的分類
        for cat in sorted(categories):
            if cat not in sorted_cats:
                sorted_cats.append(cat)
        return sorted_cats

    def _format_metric_value(
        self, metric_name: str, value: float, show_accuracy: bool = True
    ) -> str:
        """格式化指標值"""
        if value is None or value == "NaN":
            return "N/A"

        if metric_name == "Edit_dist" and show_accuracy:
            accuracy = 1.0 - value
            return f"{value:.4f} ({accuracy*100:.2f}%)"
        else:
            return f"{value:.4f}"

    def _get_metric_value(
        self, all_data: dict, metric_name: str, sub_metric: str | None = None
    ) -> float | None:
        """
        從 End2EndEval 的 all 巢狀結構提取指標值

        Args:
            all_data: result_all[element]["all"]，如 {"Edit_dist": {"ALL_page_avg": x, ...}, "TEDS": {"all": a}}
            metric_name: 指標名稱，如 "Edit_dist", "TEDS"
            sub_metric: Edit_dist 子指標，如 "ALL_page_avg", "edit_whole"
        """
        metric_data = all_data.get(metric_name)
        if metric_data is None:
            return None
        if not isinstance(metric_data, dict):
            return metric_data
        if sub_metric:
            return metric_data.get(sub_metric)
        # 非 Edit_dist 指標：取 "all" key
        return metric_data.get("all")

    def _generate_attribute_section(
        self,
        element_type: str,
        metric: str,
        data_key: str,
        include_count: bool = False,
    ) -> list[str]:
        """
        生成屬性分類統計的表格

        Args:
            element_type: 元素類型（如 "text_block"）
            metric: 指標名稱（如 "Edit_dist"）
            data_key: 資料鍵名（"group" 或 "page"）
            include_count: 是否包含數量欄（group 有，page 無）

        Returns:
            Markdown 行列表
        """
        lines: list[str] = []

        # 收集所有屬性
        all_attributes: set[str] = set()
        for model in self.models:
            model_data = self.results.get(model, {})
            element_data = model_data.get("elements", {}).get(element_type, {})
            section_data = element_data.get(data_key, {})
            metric_attrs = section_data.get(metric, {})
            all_attributes.update(metric_attrs.keys())

        if not all_attributes:
            lines.append("_無數據_")
            lines.append("")
            return lines

        # 排序：page 的 ALL 排最前面
        if data_key == "page":
            sorted_attrs = []
            if "ALL" in all_attributes:
                sorted_attrs.append("ALL")
            sorted_attrs.extend(sorted(a for a in all_attributes if a != "ALL"))
        else:
            sorted_attrs = sorted(all_attributes)

        # 表頭
        header = "| 屬性 |"
        separator = "|------|"
        if include_count:
            header += " 數量 |"
            separator += "------|"
        for model in self.models:
            header += f" {model} |"
            separator += "--------|"
        lines.append(header)
        lines.append(separator)

        # 各屬性數據
        for attr in sorted_attrs:
            row = f"| {attr} |"

            if include_count:
                count = 0
                for model in self.models:
                    model_data = self.results.get(model, {})
                    element_data = model_data.get("elements", {}).get(
                        element_type, {}
                    )
                    section_data = element_data.get(data_key, {})
                    sample_counts = section_data.get("sample_count", {})
                    if attr in sample_counts:
                        count = sample_counts[attr]
                        break
                row += f" {count} |"

            for model in self.models:
                model_data = self.results.get(model, {})
                element_data = model_data.get("elements", {}).get(
                    element_type, {}
                )
                section_data = element_data.get(data_key, {})
                value = section_data.get(metric, {}).get(attr)
                row += f" {self._format_metric_value(metric, value)} |"
            lines.append(row)

        lines.append("")
        return lines

    def _get_category_display_name(self, category: str) -> str:
        """取得分類的顯示名稱"""
        zh_name = self.CATEGORY_NAMES.get(category, category)
        return f"{zh_name} ({category})"

    def _generate_dataset_overview(self) -> str:
        """
        生成資料集概覽區塊

        Returns:
            Markdown 格式的資料集概覽字串
        """
        if not self.gt_statistics:
            return ""

        lines = []
        lines.append("## 資料集概覽")
        lines.append("")

        # 基本資訊
        lines.append("| 項目 | 數值 |")
        lines.append("|------|------|")
        lines.append(f"| 總頁數 | {self.gt_statistics.get('total_pages', 'N/A')} |")
        lines.append(
            f"| Ground Truth 來源 | {self.gt_statistics.get('gt_source', 'N/A')} |"
        )
        lines.append("")

        # Ground Truth 元素統計與匹配率
        gt_elements = self.gt_statistics.get("elements", {})
        if gt_elements:
            lines.append("### Ground Truth 元素統計與匹配率")
            lines.append("")

            # 表頭
            header = "| 元素類型 | GT 總數 |"
            separator = "|----------|---------|"
            for model in self.models:
                header += f" {model} |"
                separator += "----------|"

            lines.append(header)
            lines.append(separator)

            # 各元素類型
            for element_type, gt_count in gt_elements.items():
                row = f"| {element_type} | {gt_count} |"

                for model in self.models:
                    model_data = self.results.get(model, {})
                    element_data = model_data.get("elements", {}).get(element_type, {})
                    sample_count = element_data.get("sample_count", 0)

                    if gt_count > 0:
                        match_rate = sample_count / gt_count * 100
                        row += f" {sample_count} ({match_rate:.1f}%) |"
                    else:
                        row += f" {sample_count} (N/A) |"

                lines.append(row)

            lines.append("")

        return "\n".join(lines)

    def generate_markdown(self) -> str:
        """
        生成 Markdown 格式報告

        Returns:
            Markdown 格式的報告字串
        """
        lines = []
        lines.append("# OCR 模型評估報告")
        lines.append("")
        lines.append(f"生成時間: {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # 資料集概覽區塊
        dataset_overview = self._generate_dataset_overview()
        if dataset_overview:
            lines.append(dataset_overview)

        # 總覽區塊
        lines.append("## 總覽")
        lines.append("")

        for element_type, element_config in self.metrics_config.items():
            metrics = element_config.get("metric", [])
            if not metrics:
                continue

            lines.append(f"### {element_type}")
            lines.append("")

            # 展開 Edit_dist 為子指標
            expanded_metrics = []
            for metric in metrics:
                if metric == "Edit_dist":
                    for sub in self.EDIT_DIST_SUB_METRICS:
                        expanded_metrics.append(f"Edit_dist_{sub}")
                else:
                    expanded_metrics.append(metric)

            # 表頭
            header = "| 模型 | 樣本數 |"
            separator = "|------|--------|"
            for metric in expanded_metrics:
                # 簡化顯示名稱
                display_name = metric.replace("Edit_dist_", "")
                header += f" {display_name} |"
                separator += "--------|"

            lines.append(header)
            lines.append(separator)

            # 各模型數據
            for model in self.models:
                model_data = self.results.get(model, {})
                element_data = model_data.get("elements", {}).get(element_type, {})
                all_data = element_data.get("all", {})
                sample_count = element_data.get("sample_count", 0)
                row = f"| {model} | {sample_count} |"

                for metric in expanded_metrics:
                    # 從 End2EndEval nested all 結構讀取指標
                    if metric.startswith("Edit_dist_"):
                        sub = metric.replace("Edit_dist_", "")
                        metric_value = self._get_metric_value(all_data, "Edit_dist", sub)
                    else:
                        metric_value = self._get_metric_value(all_data, metric)
                    base_metric = "Edit_dist" if metric.startswith("Edit_dist") else metric
                    row += f" {self._format_metric_value(base_metric, metric_value)} |"

                lines.append(row)

            lines.append("")

        # 按 Annotation Attribute 分類統計
        lines.append("## 按 Annotation Attribute 分類統計")
        lines.append("")

        for element_type, element_config in self.metrics_config.items():
            metrics = element_config.get("metric", [])
            for metric in metrics:
                lines.append(f"### {element_type} - {metric} (Annotation Attribute)")
                lines.append("")
                lines.extend(
                    self._generate_attribute_section(
                        element_type, metric, "group", include_count=True
                    )
                )

        # 按 Page Attribute 分類統計
        lines.append("## 按 Page Attribute 分類統計")
        lines.append("")

        for element_type, element_config in self.metrics_config.items():
            metrics = element_config.get("metric", [])
            for metric in metrics:
                lines.append(f"### {element_type} - {metric} (Page Attribute)")
                lines.append("")
                lines.extend(
                    self._generate_attribute_section(element_type, metric, "page")
                )

        # 指標說明
        lines.append("## 指標說明")
        lines.append("")

        used_metrics = set()
        for element_config in self.metrics_config.values():
            used_metrics.update(element_config.get("metric", []))

        for metric in sorted(used_metrics):
            description = self.METRIC_DESCRIPTIONS.get(metric, "")
            if description:
                lines.append(f"- **{metric}**: {description}")

        lines.append("")

        return "\n".join(lines)

    def generate_json(self) -> dict:
        """
        生成 JSON 結構化報告

        Returns:
            結構化的報告字典
        """
        # 提取配置中的指標列表
        config_metrics = {}
        for element_type, element_config in self.metrics_config.items():
            config_metrics[element_type] = element_config.get("metric", [])

        result = {
            "generated_at": self.generated_at.isoformat(),
            "config": {"metrics": config_metrics},
        }

        # 加入資料集概覽
        if self.gt_statistics:
            result["dataset_overview"] = self.gt_statistics

        result["models"] = self.results

        return result

    def generate_errors_analysis(self) -> dict:
        """
        生成錯誤分析結構化報告

        Returns:
            錯誤分析字典，包含摘要和詳細錯誤
        """
        analysis = {
            "generated_at": self.generated_at.isoformat(),
            "summary": {},
            "errors_by_data_source": {},
        }

        gt_elements = self.gt_statistics.get("elements", {})

        # 計算摘要
        for element_type in gt_elements:
            gt_count = gt_elements[element_type]
            analysis["summary"][element_type] = {
                "gt_total": gt_count,
                "models": {},
            }

            for model in self.models:
                model_data = self.results.get(model, {})
                element_data = model_data.get("elements", {}).get(element_type, {})
                sample_count = element_data.get("sample_count", 0)

                # 計算錯誤統計
                model_errors = self.errors_data.get(model, {}).get(element_type, {})
                error_count = sum(len(items) for items in model_errors.values())
                unmatched_count = sum(
                    len([i for i in items if i.get("error_type") == "unmatched"])
                    for items in model_errors.values()
                )
                mismatched_count = error_count - unmatched_count

                analysis["summary"][element_type]["models"][model] = {
                    "total_samples": sample_count,
                    "error_count": error_count,
                    "unmatched_count": unmatched_count,
                    "mismatched_count": mismatched_count,
                    "accuracy": (sample_count - error_count) / sample_count
                    if sample_count > 0
                    else 0,
                }

        # 按 data_source 組織詳細錯誤
        for model in self.models:
            analysis["errors_by_data_source"][model] = {}

            model_errors = self.errors_data.get(model, {})
            for element_type, ds_errors in model_errors.items():
                if ds_errors:
                    analysis["errors_by_data_source"][model][element_type] = {}

                    sorted_ds = self._get_sorted_categories(set(ds_errors.keys()))
                    for data_source in sorted_ds:
                        items = ds_errors[data_source]
                        analysis["errors_by_data_source"][model][element_type][
                            data_source
                        ] = {
                            "count": len(items),
                            "items": items,
                        }

        return analysis

    def save_reports(
        self,
        output_dir: str,
        base_name: str = "ocr_comparison_report",
        generate_markdown: bool = True,
        generate_json: bool = True,
        generate_errors: bool = True,
    ) -> dict[str, str]:
        """
        儲存報告到檔案

        Args:
            output_dir: 輸出目錄
            base_name: 報告檔案基礎名稱
            generate_markdown: 是否生成 Markdown 報告
            generate_json: 是否生成 JSON 報告
            generate_errors: 是否生成錯誤分析 JSON

        Returns:
            生成的檔案路徑字典
        """
        os.makedirs(output_dir, exist_ok=True)
        saved_files = {}

        if generate_markdown:
            md_path = os.path.join(output_dir, f"{base_name}.md")
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(self.generate_markdown())
            saved_files["markdown"] = md_path
            print(f"Markdown 報告已儲存至: {md_path}")

        if generate_json:
            json_path = os.path.join(output_dir, f"{base_name}.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(self.generate_json(), f, indent=2, ensure_ascii=False)
            saved_files["json"] = json_path
            print(f"JSON 報告已儲存至: {json_path}")

        if generate_errors and self.errors_data:
            errors_path = os.path.join(output_dir, f"{base_name}_errors.json")
            with open(errors_path, "w", encoding="utf-8") as f:
                json.dump(
                    self.generate_errors_analysis(), f, indent=2, ensure_ascii=False
                )
            saved_files["errors"] = errors_path
            print(f"錯誤分析報告已儲存至: {errors_path}")

        return saved_files
