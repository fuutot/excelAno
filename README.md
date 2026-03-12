# excelAno
Excel形式のアノテーションファイルを扱うライブラリ

**excelAno** は，Excel形式のアノテーションファイルを効率的に扱うためのPythonライブラリです．

アノテーターが使い慣れたExcelとエンジニア，研究者が使いやすいCSVの間の変換を行います．

## 主な機能
- **アノテーションファイルの読み込み**: Excel形式のアノテーションファイルを読み込む．
- **バリデーション**: 列名，データ型，必須項目，許容されるラベル値（例: `['Positive', 'Negative']`）を事前に定義し，入力ミスを自動検知．
- **スムーズなフォーマット変換**: 読み込んだデータを`CSV` としてエクスポート可能．
- **評価結果の一致度能評価**: アノテーションの一致度を表す，kappa係数を計算可能．
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

