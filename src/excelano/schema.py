from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import pandas as pd

if TYPE_CHECKING:
    from excelano.annotation_data import AnnotationData
    from excelano.template import Template


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

    def cast_dtype(self, series: pd.Series) -> pd.Series:
        """Seriesをこの列のdtypeに型キャストする

        Null値が含まれる場合は、非Null値のみ型キャストし、Null値はそのまま保持する。

        args:
            series: キャスト対象のpandas Series
        returns:
            pd.Series: 型キャスト後のSeries（dtypeが未設定の場合はそのまま返す）
        """
        if self.dtype is not None:
            if series.isna().any():
                result = series.copy()
                mask = series.notna()
                result[mask] = series[mask].astype(self.dtype)
                return result
            return series.astype(self.dtype)
        return series

    def validate(self, series: pd.Series) -> list[str]:
        """Seriesを検証し、エラーメッセージのリストを返す

        行番号はデータ行の1行目からの通し番号（1始まり）で出力される。

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

    def cast_dtypes(self, data: AnnotationData | Template) -> AnnotationData | Template:
        """AnnotationData/Templateの各列をColumnのdtypeに型キャストする

        args:
            data: キャスト対象のAnnotationDataまたはTemplate
        returns:
            AnnotationData | Template: 型キャスト後のオブジェクト（元のオブジェクトは変更されない）
        """
        data = data.copy()
        for col in self.columns:
            if col.dtype is not None and col.name in data.columns:
                data[col.name] = col.cast_dtype(data[col.name])
        return data

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

    def validate(self, data: AnnotationData | Template) -> list[str]:
        """AnnotationData/Template全体を検証し、エラーメッセージのリストを返す

        型キャスト（Columnにdtypeが設定されている場合）を行った上でバリデーションを実行する。
        AnnotationDataの場合はアノテーション対象列にNull値がないことを確認する（アノテーション漏れ検知）。
        Templateの場合はアノテーション対象列が全てNull値であることを確認する。

        args:
            data: 検証対象のAnnotationDataまたはTemplate（型キャストにより内容が変更される場合がある）
        returns:
            list[str]: エラーメッセージのリスト（エラーがなければ空リスト）
        """
        from excelano.annotation_data import AnnotationData
        from excelano.template import Template

        errors: list[str] = []

        # 型キャスト
        for col in self.columns:
            if col.dtype is not None and col.name in data.columns:
                try:
                    data[col.name] = col.cast_dtype(data[col.name])
                except (ValueError, TypeError) as e:
                    errors.append(f"列 '{col.name}' の型キャストに失敗しました（{col.dtype.__name__}）: {e}")

        # ID列の一意性チェック
        if data.duplicated(subset=self.id_cols).any():
            errors.append("id_colsで指定された列の組み合わせで一意に識別できません。")

        # AnnotationData: アノテーション対象列にNull値がないことを確認
        if isinstance(data, AnnotationData):
            for col_name in self.annotation_cols:
                if col_name in data.columns:
                    null_mask = data[col_name].isnull()
                    for i, is_null in enumerate(null_mask, start=1):
                        if is_null:
                            errors.append(
                                f"列 '{col_name}' の {i} 行目: Null値は許容されていません。アノテーション漏れの可能性があります。"
                            )

        # Template: アノテーション対象列が全てNull値であることを確認
        if isinstance(data, Template):
            for col_name in self.annotation_cols:
                if col_name in data.columns and data[col_name].notnull().any():
                    errors.append(
                        f"列 '{col_name}' にNull以外の値が含まれています。アノテーション対象の列は空にしてください。"
                    )

        # 各列のバリデーション
        for col in self.columns:
            if col.name in data.columns:
                errors.extend(col.validate(data[col.name]))

        return errors
