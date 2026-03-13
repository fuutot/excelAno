"""テンプレート作成の例

CSVデータからアノテーション用のExcelテンプレートを生成します．
生成されたExcelには，ドロップダウンリスト・シート保護・書式が自動設定されます．
"""

from pathlib import Path

from excelano.schema import Column, Schema
from excelano.template import Template

# --- スキーマを定義：各列の型や許容値を指定 ---
schema = Schema(
    columns=[
        Column(name="id", dtype=int),
        Column(name="text", dtype=str),
        Column(name="label", dtype=str, allowed_values=["positive", "negative", "neutral"]),
    ],
    id_cols=["id"],
    annotation_cols=["label"],
)

# --- CSVからテンプレートを作成 ---
data_path = Path(__file__).parent / "sample_data" / "data.csv"
template = Template.from_csv(
    file_path=str(data_path),
    id_cols=["id"],
    annotation_cols=["label"],
    schema=schema,
)

# --- Excelに出力 ---
output_path = Path(__file__).parent / "output" / "annotation_template.xlsx"
output_path.parent.mkdir(exist_ok=True)
template.to_excel(str(output_path))

print(f"テンプレートを作成しました: {output_path}")
