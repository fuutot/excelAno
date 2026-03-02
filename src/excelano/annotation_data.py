from __future__ import annotations

import numpy as np
import pandas as pd

from excelano.schema import Schema, SchemaValidationError


class MissingValueError(ValueError):
    """アノテーションデータに欠損値が含まれている場合に発生するエラー"""

    pass


class AnnotationTargetMismatchError(ValueError):
    """評価者間で評価対象が一致しない場合に発生するエラー"""

    pass


class AnnotationData(pd.DataFrame):
    # TODO: DataFrameを継承する際の注意点を読む
    # https://pandas.pydata.org/docs/development/extending.html#subclassing-pandas-data-structures

    _metadata = ["annotated_cols", "id_cols", "schema"]  # pandasのDataFrameに属性を保持させるための変数

    @property
    def _constructor(self):
        return AnnotationData

    @staticmethod
    def from_excel(
        file_path,
        annotated_cols: list[str],
        id_cols: list[str],
        schema: Schema | None = None,
    ) -> AnnotationData:
        """
        エクセル形式のアノテーションデータを読み込むメソッド
        args:
            file_path: エクセルファイルのパス
            annotated_cols: アノテーション対象の列名のリスト
            id_cols: 評価対象を一意に識別する列名のリスト
            schema: バリデーション用のSchemaオブジェクト（任意）
        returns:
            AnnotationData: 読み込んだアノテーションデータ
        """
        # str型など，Noneに対応できない型を指定した場合，エラーになるため，先に読み込んでから型変換する
        df = pd.read_excel(file_path)

        # アノテーション対象のデータに欠損値がある場合，エラーを発生させる
        if df[annotated_cols].isnull().any().any():
            raise MissingValueError("アノテーションデータに欠損値が含まれています。")

        # id_colsで一意に識別できるか確認
        if df.duplicated(subset=id_cols).any():
            raise ValueError("id_colsで指定された列の組み合わせで一意に識別できません。")

        # Schemaによる型キャストとバリデーション
        if schema is not None:
            df = schema.cast_dtypes(df)
            errors = schema.validate(df)
            if errors:
                raise SchemaValidationError(errors)

        result = AnnotationData(df)
        result.annotated_cols = annotated_cols
        result.id_cols = sorted(
            id_cols
        )  # MultipleAnnotationDataでのソート作業にて，id_colsの順序が異なると正しく対応付けできないため，id_colsはソートして保持する
        result.schema = schema
        return result


class MultipleAnnotationData:
    """複数のアノテーションデータをまとめて管理するクラス"""

    def __init__(self, annotation_data_list: list[AnnotationData]):
        # すべてのAnnotationDataが同じid_colsを持っていない場合，同じアノテーション対象を持っているとは言えないため，エラーを発生させる
        has_same_id_cols = len(set(tuple(data.id_cols) for data in annotation_data_list)) == 1
        if not has_same_id_cols:
            raise AnnotationTargetMismatchError(
                "すべてのAnnotationDataが同じid_colsを持っている必要があります。"
                "すべてのAnnotationDataが同じ評価対象に対してアノテーションを行っていることを確認してください。"
            )

        # すべてのAnnotationDataが同じアノテーション対象を持っているか確認
        id_cols: list[str] = annotation_data_list[0].id_cols
        base_ids = annotation_data_list[0].sort_values(by=id_cols)[id_cols].reset_index(drop=True)
        has_same_targets = all(
            data.sort_values(by=id_cols)[id_cols].reset_index(drop=True).equals(base_ids)
            for data in annotation_data_list[1:]
        )
        if not has_same_targets:
            raise AnnotationTargetMismatchError(
                "すべてのAnnotationDataが同じ評価対象を持っている必要があります。"
                "すべてのAnnotationDataが同じ評価対象に対してアノテーションを行っていることを確認してください。"
            )

        if len(annotation_data_list) < 2:
            raise ValueError("複数のAnnotationDataを提供する必要があります。")

        self.annotation_data_list = annotation_data_list
        self.id_cols: list[str] = id_cols

    def compute_kappa(self, target_col: str) -> float:
        """評価者間の合致率をカッパ係数で計算するメソッド

        評価者が2人の場合はCohen's kappa，3人以上の場合はFleiss' kappaを使用する。
        それぞれ評価者数に適した計算手法を自動で選択することで，適切な合致率を返す。

        args:
            target_col: カッパ係数を計算する対象の列名（annotated_colsに含まれている必要がある）
        returns:
            float: カッパ係数
        raises:
            AnnotationTargetMismatchError: 評価者間で評価対象のセットが一致しない場合
        """
        # id_colsでデータをソートして整列することで，行順が異なっても正しく評価対象を対応付ける
        aligned = [data.sort_values(by=self.id_cols).reset_index(drop=True) for data in self.annotation_data_list]

        # ID整列済みのデータからtarget_col列の評価値を取得する
        ratings = [data[target_col].tolist() for data in aligned]

        if len(self.annotation_data_list) == 2:
            # 評価者が2人の場合はCohen's kappaを使用する
            return self._compute_cohen_kappa(ratings[0], ratings[1])
        else:
            # 評価者が3人以上の場合はFleiss' kappaを使用する
            return self._compute_fleiss_kappa(ratings)

    @staticmethod
    def _compute_cohen_kappa(ratings1: list, ratings2: list) -> float:
        """Cohen's kappa係数を計算する（2評価者向け）

        偶然の一致を補正した上で，評価者間の合致率を0～1のスコアとして返す。

        args:
            ratings1: 評価者1の評価値のリスト
                     例: [1, 0, 1, 0]（4つのアイテムに対する評価値）
            ratings2: 評価者2の評価値のリスト
                     例: [1, 0, 1, 0]（同じアイテムに対する評価値）
        returns:
            float: Cohen's kappa係数（-1～1の範囲）
        """
        n = len(ratings1)
        categories = sorted(set(ratings1) | set(ratings2))
        cat_idx = {c: i for i, c in enumerate(categories)}
        k = len(categories)

        # 混同行列を構築する
        matrix = np.zeros((k, k), dtype=float)
        for a, b in zip(ratings1, ratings2):
            matrix[cat_idx[a]][cat_idx[b]] += 1

        # 実際の一致率（対角成分の合計）
        po = np.trace(matrix) / n
        # 偶然による期待一致率（行・列の周辺分布の積の合計）
        row_marginals = matrix.sum(axis=1) / n
        col_marginals = matrix.sum(axis=0) / n
        pe = float(np.dot(row_marginals, col_marginals))

        return (po - pe) / (1 - pe)

    @staticmethod
    def _compute_fleiss_kappa(ratings: list[list]) -> float:
        """Fleiss' kappa係数を計算する（3評価者以上向け）

        複数評価者の評価データを行列に変換し，偶然の一致を補正した合致率を返す。

        args:
            ratings: 複数評価者の評価値のリスト。各評価者の評価値を要素とするリストのリスト。
                     ratings[i]は評価者iの全アイテムに対する評価値のリスト
                     例: [[1, 0, 1], [1, 0, 1], [1, 1, 1]]
                        3つのアイテムに対して3評価者が評価した値
                        ratings[0] = [1, 0, 1]（評価者1の評価）
                        ratings[1] = [1, 0, 1]（評価者2の評価）
                        ratings[2] = [1, 1, 1]（評価者3の評価）
        returns:
            float: Fleiss' kappa係数（-1～1の範囲）
        """
        n_raters = len(ratings)
        n_subjects = len(ratings[0])
        categories = sorted(set(r for rater in ratings for r in rater))
        k = len(categories)
        cat_idx = {c: i for i, c in enumerate(categories)}

        # 各アイテムに対するカテゴリ別の評価者数を集計した行列（N×C）を構築する
        counts = np.zeros((n_subjects, k), dtype=float)
        for rater_ratings in ratings:
            for i, rating in enumerate(rater_ratings):
                counts[i][cat_idx[rating]] += 1

        # 各カテゴリjに対するすべての評価の中での割合p_jを計算する
        p_j = counts.sum(axis=0) / (n_subjects * n_raters)

        # 各アイテムiにおける評価者間の一致度P_iを計算する
        P_i = (np.sum(counts**2, axis=1) - n_raters) / (n_raters * (n_raters - 1))

        # 全アイテムの平均一致率と偶然による期待一致率を計算する
        P_bar = float(P_i.mean())
        P_e_bar = float(np.sum(p_j**2))

        return (P_bar - P_e_bar) / (1 - P_e_bar)
