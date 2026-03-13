"""アノテーション結果の読み込み・検証の例

アノテーターが記入したExcelファイルを読み込み，スキーマに基づいてバリデーションを行います．
この例では，サンプルの記入済みExcelを動的に生成してから読み込みます．
"""

from pathlib import Path

import pandas as pd

from excelano.annotation_data import AnnotationData
from excelano.schema import Column, Schema, SchemaValidationError

# --- サンプルの記入済みExcelを生成（実際のワークフローでは不要） ---
sample_data = pd.DataFrame(
    {
        "id": [1, 2, 3, 4, 5],
        "text": [
            "この商品はとても良かったです",
            "品質に問題がありました",
            "普通でした",
            "デザインが気に入りました",
            "期待外れでした",
        ],
        "label": ["positive", "negative", "neutral", "positive", "negative"],
    }
)
sample_excel_path = Path(__file__).parent / "output" / "annotated_sample.xlsx"
sample_excel_path.parent.mkdir(exist_ok=True)
sample_data.to_excel(str(sample_excel_path), index=False)

# --- スキーマを定義 ---
schema = Schema(
    columns=[
        Column(name="id", dtype=int),
        Column(name="text", dtype=str),
        Column(name="label", dtype=str, allowed_values=["positive", "negative", "neutral"]),
    ],
    id_cols=["id"],
    annotation_cols=["label"],
)

# --- アノテーション結果を読み込み（スキーマによる自動検証付き） ---
try:
    data = AnnotationData.from_excel(
        file_path=str(sample_excel_path),
        annotated_cols=["label"],
        id_cols=["id"],
        schema=schema,
    )
    print("バリデーション成功!")
    print(data)

    # --- pandas DataFrameとして操作可能 ---
    csv_path = Path(__file__).parent / "output" / "annotated_sample.csv"
    data.to_csv(str(csv_path), index=False)
    print(f"\nCSVに変換しました: {csv_path}")

except SchemaValidationError as e:
    print(f"バリデーションエラー: {e.errors}")
