from dataclasses import dataclass, field
from typing import Any

import pandas as pd


class SchemaValidationError(ValueError):
    """Schemaバリデーションでエラーが検出された場合に発生するエラー"""

    def __init__(self, errors: list[str]):
        self.errors = errors
        message = "\n".join(errors)
        super().__init__(message)


@dataclass
class Column:
    """各列ごとに許容されるデータを管理するクラス

    Attributes:
        name: 列名
        dtype: 許容される型（例: str, int, float）
        allowed_values: 許容される値のリスト（例: [0, 1]）
    """

    name: str
    dtype: type | None = None
    allowed_values: list[Any] | None = None

    def validate(self, series: pd.Series) -> list[str]:
        """Seriesを検証し、エラーメッセージのリストを返す

        args:
            series: 検証対象のpandas Series
        returns:
            list[str]: エラーメッセージのリスト（エラーがなければ空リスト）
        """
        errors: list[str] = []

        if self.dtype is not None:
            for i, value in enumerate(series, start=1):
                if pd.notna(value):
                    try:
                        self.dtype(value)
                    except (ValueError, TypeError):
                        errors.append(
                            f"列 '{self.name}' の {i} 行目: 値 '{value}' を型 '{self.dtype.__name__}' に変換できません。"
                        )

        if self.allowed_values is not None:
            for i, value in enumerate(series, start=1):
                if pd.notna(value) and value not in self.allowed_values:
                    errors.append(
                        f"列 '{self.name}' の {i} 行目: 値 '{value}' は許容されていません。許容値: {self.allowed_values}"
                    )

        return errors


@dataclass
class Schema:
    """アノテーションファイル全体で許容される状態を管理するクラス

    Attributes:
        columns: Columnオブジェクトのリスト
        id_cols: IDとなる列名のリスト
        annotation_cols: アノテーション対象列名のリスト
    """

    columns: list[Column]
    id_cols: list[str]
    annotation_cols: list[str]
    _column_map: dict[str, Column] = field(init=False, repr=False)

    def __post_init__(self):
        self._column_map = {col.name: col for col in self.columns}

    def get_dtype_dict(self) -> dict[str, type]:
        """Columnからdtype辞書を生成する

        returns:
            dict[str, type]: 列名と型の辞書（dtypeが設定されたColumnのみ）
        """
        return {col.name: col.dtype for col in self.columns if col.dtype is not None}

    def get_column(self, col_name: str) -> Column | None:
        """列名からColumnオブジェクトを取得する

        args:
            col_name: 列名
        returns:
            Column | None: Columnオブジェクト（存在しない場合はNone）
        """
        return self._column_map.get(col_name)

    def validate(self, df: pd.DataFrame) -> list[str]:
        """DataFrame全体を検証し、エラーメッセージのリストを返す

        args:
            df: 検証対象のDataFrame
        returns:
            list[str]: エラーメッセージのリスト（エラーがなければ空リスト）
        """
        errors: list[str] = []

        # ID列の一意性チェック
        if df.duplicated(subset=self.id_cols).any():
            errors.append("id_colsで指定された列の組み合わせで一意に識別できません。")

        # 各列のバリデーション
        for col in self.columns:
            if col.name in df.columns:
                errors.extend(col.validate(df[col.name]))

        return errors
