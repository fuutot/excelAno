# excelAno
Excel形式のアノテーションファイルを扱うライブラリ

**excelAno** は，Excel形式のアノテーションファイルを効率的に扱うためのPythonライブラリです．

アノテーターが使い慣れたExcelとエンジニア，研究者が使いやすいCSVの間の変換を行います．

## 主な機能
- **アノテーションファイルの読み込み**: Excel形式のアノテーションファイルを読み込む．
- **バリデーション**: 列名，データ型，必須項目，許容されるラベル値（例: `['Positive', 'Negative']`）を事前に定義し，入力ミスを自動検知．
- **スムーズなフォーマット変換**: 読み込んだデータを`CSV` としてエクスポート可能．
- **評価結果の一致度評価**: アノテーションの一致度を表す，kappa係数を計算可能．
- **テンプレート作成**: 作業者向けに，ドロップダウンリスト（入力規則）などを設定した空のアノテーション用Excelをプログラムから生成．

## インストール

```bash
pip install excelano
```

## 使用例

完全なコードは [`examples/`](examples/) ディレクトリを参照してください．

### 1. アノテーション用テンプレートを作成する

アノテーターに配布するExcelテンプレートを，CSVデータから生成します．
ドロップダウンリストやシート保護が自動設定されるため，入力ミスを防げます．

> 完全なコード: [`examples/01_create_template.py`](examples/01_create_template.py)

```python
from excelano.schema import Column, Schema
from excelano.template import Template

# スキーマを定義：各列の型や許容値を指定
schema = Schema(
    columns=[
        Column(name="id", dtype=int),
        Column(name="text", dtype=str),
        Column(name="label", dtype=str, allowed_values=["positive", "negative", "neutral"]),
    ],
    id_cols=["id"],
    annotation_cols=["label"],
)

# CSVからテンプレートを作成
template = Template.from_csv(
    file_path="data.csv",
    id_cols=["id"],
    annotation_cols=["label"],
    schema=schema,
)

# Excelに出力（ドロップダウン・シート保護・書式が自動設定される）
template.to_excel("annotation_template.xlsx")
```

### 2. アノテーション結果を読み込み・検証する

アノテーターが記入したExcelファイルを読み込みます．
スキーマを指定すると，欠損値や不正な値がある場合にエラーが発生します．

> 完全なコード: [`examples/02_load_and_validate.py`](examples/02_load_and_validate.py)

```python
from excelano.annotation_data import AnnotationData
from excelano.schema import Column, Schema

schema = Schema(
    columns=[
        Column(name="id", dtype=int),
        Column(name="text", dtype=str),
        Column(name="label", dtype=str, allowed_values=["positive", "negative", "neutral"]),
    ],
    id_cols=["id"],
    annotation_cols=["label"],
)

data = AnnotationData.from_excel(
    file_path="annotated.xlsx",
    annotated_cols=["label"],
    id_cols=["id"],
    schema=schema,
)

# pandas DataFrameとして操作可能
print(data.head())
data.to_csv("annotated.csv", index=False)
```

### 3. アノテーターの一致度を評価する（kappa係数）

複数のアノテーターの結果を比較し，評価の一致度をkappa係数で測定します．
2人の場合はCohen's kappa，3人以上の場合はFleiss' kappaが自動的に選択されます．

> 完全なコード: [`examples/03_compute_kappa.py`](examples/03_compute_kappa.py)

```python
from excelano.annotation_data import AnnotationData, MultipleAnnotationData

# 各アノテーターのデータを読み込み
annotator_a = AnnotationData.from_excel(
    "annotator_a.xlsx", annotated_cols=["label"], id_cols=["id"]
)
annotator_b = AnnotationData.from_excel(
    "annotator_b.xlsx", annotated_cols=["label"], id_cols=["id"]
)

# 一致度を計算（2人 → Cohen's kappa）
multi = MultipleAnnotationData([annotator_a, annotator_b])
kappa = multi.compute_kappa("label")
print(f"Cohen's kappa: {kappa:.3f}")
```