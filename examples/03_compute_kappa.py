"""一致度評価（kappa係数）の例

複数のアノテーターの結果を比較し，評価の一致度をkappa係数で測定します．
2人の場合はCohen's kappa，3人以上の場合はFleiss' kappaが自動的に選択されます．
この例では，サンプルの記入済みExcelを動的に生成してから計算します．
"""

from pathlib import Path

import pandas as pd

from excelano.annotation_data import AnnotationData, MultipleAnnotationData

# --- サンプルの記入済みExcelを生成（実際のワークフローでは不要） ---
output_dir = Path(__file__).parent / "output"
output_dir.mkdir(exist_ok=True)

texts = [
    "この商品はとても良かったです",
    "品質に問題がありました",
    "普通でした",
    "デザインが気に入りました",
    "期待外れでした",
]

annotator_a_data = pd.DataFrame(
    {"id": [1, 2, 3, 4, 5], "text": texts, "label": ["positive", "negative", "neutral", "positive", "negative"]}
)
annotator_b_data = pd.DataFrame(
    {"id": [1, 2, 3, 4, 5], "text": texts, "label": ["positive", "negative", "positive", "positive", "negative"]}
)

path_a = output_dir / "annotator_a.xlsx"
path_b = output_dir / "annotator_b.xlsx"
annotator_a_data.to_excel(str(path_a), index=False)
annotator_b_data.to_excel(str(path_b), index=False)

# --- 各アノテーターのデータを読み込み ---
data_a = AnnotationData.from_excel(str(path_a), annotated_cols=["label"], id_cols=["id"])
data_b = AnnotationData.from_excel(str(path_b), annotated_cols=["label"], id_cols=["id"])

# --- 一致度を計算（2人 → Cohen's kappa） ---
multi = MultipleAnnotationData([data_a, data_b])
kappa = multi.compute_kappa("label")
print(f"Cohen's kappa: {kappa:.3f}")
