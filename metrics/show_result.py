from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List

import pandas as pd
from tabulate import tabulate


def show_result(results):
    for metric_name in results.keys():
        print(f'{metric_name}:')
        score_table = [[k,v] for k,v in results[metric_name].items()]
        print(tabulate(score_table))
        print('='*100)

def sort_nested_dict(d):
    # If it's a dictionary, recursively sort it
    if isinstance(d, dict):
        # Sort the current dictionary
        sorted_dict = {k: sort_nested_dict(v) for k, v in sorted(d.items())}
        return sorted_dict
    # If not a dictionary, return directly
    return d

def get_full_labels_results(samples):
    if not samples:
        return {}
    label_group_dict = defaultdict(lambda: defaultdict(list))
    for sample in samples:
        label_list = []
        if not sample.get("gt_attribute"):
            continue
        for anno in sample["gt_attribute"]:
            for k,v in anno.items():
                label_list.append(k+": "+str(v))
        for label_name in list(set(label_list)):  # Currently if there are merged cases, calculate based on the set of all labels involved after merging
            for metric, score in sample['metric'].items():
                label_group_dict[label_name][metric].append(score)

    print('----Anno Attribute---------------')
    result = {}
    result['sample_count'] = {}
    for attribute in label_group_dict.keys():
        for metric, scores in label_group_dict[attribute].items():
            mean_score = sum(scores) / len(scores)
            if not result.get(metric):
                result[metric] = {}
            result[metric][attribute] = mean_score
            result['sample_count'][attribute] = len(scores)
    result = sort_nested_dict(result)
    show_result(result)
    return result

# def get_page_split(samples, page_info):    # Sample level metric
#     if not page_info:
#         return {}
#     page_split_dict = defaultdict(lambda: defaultdict(list)) 
#     for sample in samples:
#         img_name = sample['img_id'] if sample['img_id'].endswith('.jpg') else '_'.join(sample['img_id'].split('_')[:-1])
#         page_info_s = page_info[img_name]
#         if not sample.get('metric'):
#             continue
#         for metric, score in sample['metric'].items():
#             for k,v in page_info_s.items():
#                 if isinstance(v, list): # special issue
#                     for special_issue in v:
#                         if 'table' not in special_issue:  # Table-related special fields have duplicates
#                             page_split_dict[metric][special_issue].append(score)
#                 else:
#                     page_split_dict[metric][k+": "+str(v)].append(score)
    
#     print('----Page Attribute---------------')
#     result = {}
#     result['sample_count'] = {}
#     for metric in page_split_dict.keys():
#         for attribute, scores in page_split_dict[metric].items():
#             mean_score = sum(scores) / len(scores)
#             if not result.get(metric):
#                 result[metric] = {}
#             result[metric][attribute] = mean_score
#             result['sample_count'][attribute] = len(scores)
#     result = sort_nested_dict(result)
#     show_result(result)
#     return result

def get_page_split(samples, page_info):   # Page level metric
    if not page_info:
        return {}
    result_list = defaultdict(list)
    for sample in samples:
        img_name = sample['img_id'][:-4] if sample['img_id'].endswith('.jpg') or sample['img_id'].endswith('.png') else '_'.join(sample['img_id'].split('_')[:-1])
        page_info_s = page_info[img_name]
        if not sample.get('metric'):
            continue
        for metric, score in sample['metric'].items():
            gt = sample['norm_gt'] if sample.get('norm_gt') else sample['gt']
            pred = sample['norm_pred'] if sample.get('norm_pred') else sample['pred']
            result_list[metric].append({
                'image_name': img_name,
                'metric': metric,
                'attribute': 'ALL',
                'score': score,
                'upper_len': max(len(gt), len(pred))
            })
            for k,v in page_info_s.items():
                if isinstance(v, list): # special issue
                    for special_issue in v:
                        if 'table' not in special_issue:  # Table-related special fields have duplicates
                            result_list[metric].append({
                                'image_name': img_name,
                                'metric': metric,
                                'attribute': special_issue,
                                'score': score,
                                'upper_len': max(len(gt), len(pred))
                            })
                else:
                    result_list[metric].append({
                        'image_name': img_name,
                        'metric': metric,
                        'attribute': k+": "+str(v),
                        'score': score,
                        'upper_len': max(len(gt), len(pred))
                    })
    
    # Page level logic, accumulation is only done within pages, and mean operation is performed between pages
    result = {}
    if result_list.get('Edit_dist'):   # 只有Edit_dist需要进行page level的计算
        df = pd.DataFrame(result_list['Edit_dist'])
        up_total_avg = df.groupby(["image_name", "attribute"]).apply(lambda x: (x["score"]*x['upper_len']).sum() / x['upper_len'].sum()).groupby('attribute').mean()  # At page level, accumulate edits, denominator is sum of max(gt, pred) from each sample
        # up_total_avg = df.groupby(["attribute"]).apply(lambda x: (x["score"]*x['upper_len']).sum() / x['upper_len'].sum()) # whole_level
        result['Edit_dist'] = up_total_avg.to_dict()
    for metric in result_list.keys():
        if metric == 'Edit_dist':
            continue
        df = pd.DataFrame(result_list[metric])
        page_avg = df.groupby(["image_name", "attribute"]).apply(lambda x: x["score"].mean()).groupby('attribute').mean() # 页面内部平均以后，再页面间的平均
        result[metric] = page_avg.to_dict()

    # 計算每個 attribute 的唯一頁面數（頁數）
    # 從任一 metric 的 DataFrame 取得，因頁面集合與 metric 無關
    first_metric = next(iter(result_list), None)
    if first_metric is not None:
        df = pd.DataFrame(result_list[first_metric])
        result["sample_count"] = (
            df.groupby("attribute")["image_name"].nunique().to_dict()
        )

    result = sort_nested_dict(result)
    # print('----Page Attribute---------------')
    show_result(result)
    return result


def get_data_source_summary(
    samples: list, page_info: dict
) -> dict[str, dict[str, Any]]:
    """
    按 data_source 分類彙總評估結果

    此函數專門處理按文件來源（paper, presentation, handwriting 等）分類的統計，
    支援多種指標的彙總計算。

    Args:
        samples: 評估樣本列表，每個樣本包含 img_id, metric, Edit_num, upper_len 等欄位
        page_info: 頁面資訊字典，key 為圖片名稱（不含副檔名），value 包含 data_source 等屬性

    Returns:
        按 data_source 分組的統計結果，格式為：
        {
            "paper": {
                "count": 26,
                "metrics": {
                    "Edit_dist": {"value": 0.0167, "accuracy": 0.9833},
                    "TEDS": {"value": 0.8912}
                }
            },
            "presentation": {...},
            ...
        }
    """
    if not samples or not page_info:
        return {}

    # 按 data_source 分組收集樣本
    data_source_samples = defaultdict(list)

    for sample in samples:
        # 從 img_id 取得圖片名稱（去除副檔名和索引後綴）
        img_id = sample.get("img_id", "")
        if img_id.endswith(".jpg") or img_id.endswith(".png"):
            img_name = img_id[:-4]
        else:
            # 處理帶有數字索引後綴的情況，如 "image_0" -> "image"
            parts = img_id.rsplit("_", 1)
            if len(parts) == 2 and parts[1].isdigit():
                img_name = parts[0]
            else:
                img_name = img_id

        if img_name not in page_info:
            continue

        data_source = page_info[img_name].get("data_source", "unknown")
        data_source_samples[data_source].append(sample)

    # 計算每個 data_source 的統計
    result = {}

    for data_source, ds_samples in data_source_samples.items():
        if not ds_samples:
            continue

        count = len(ds_samples)
        metrics_result = {}

        # 處理 Edit_dist 指標（需要特殊計算 accuracy）
        if any(s.get("Edit_num") is not None for s in ds_samples):
            total_edit = sum(s.get("Edit_num", 0) for s in ds_samples)
            total_upper_len = sum(s.get("upper_len", 0) for s in ds_samples)

            if total_upper_len > 0:
                edit_dist_value = total_edit / total_upper_len
                accuracy = 1.0 - edit_dist_value
            else:
                edit_dist_value = 0
                accuracy = 1.0

            metrics_result["Edit_dist"] = {"value": edit_dist_value, "accuracy": accuracy}

        # 處理其他指標（TEDS, CDM, BLEU, METEOR 等）
        for sample in ds_samples:
            if not sample.get("metric"):
                continue
            for metric_name, metric_value in sample["metric"].items():
                if metric_name == "Edit_dist":
                    continue  # 已經處理過
                if metric_name not in metrics_result:
                    metrics_result[metric_name] = {"values": []}
                if isinstance(metric_value, (int, float)) and metric_value != "NaN":
                    metrics_result[metric_name]["values"].append(metric_value)

        # 計算其他指標的平均值
        for metric_name in list(metrics_result.keys()):
            if metric_name == "Edit_dist":
                continue
            values = metrics_result[metric_name].get("values", [])
            if values:
                metrics_result[metric_name] = {"value": sum(values) / len(values)}
            else:
                del metrics_result[metric_name]

        result[data_source] = {"count": count, "metrics": metrics_result}

    return result
