import pandas as pd


class MissingValueError(ValueError):
    """アノテーションデータに欠損値が含まれている場合に発生するエラー"""

    pass


class AnnotationData(pd.DataFrame):
    # TODO: DataFrameを継承する際の注意点を読む
    # https://pandas.pydata.org/docs/development/extending.html#subclassing-pandas-data-structures

    _metadata = ["annotated_cols"]  # pandasのDataFrameに属性を保持させるための変数

    @property
    def _constructor(self):
        return AnnotationData

    @staticmethod
    def from_excel(
        file_path, dtype: dict[str, type], annotated_cols: list[str]
    ) -> "AnnotationData":
        """
        エクセル形式のアノテーションデータを読み込むメソッド
        args:
            file_path: エクセルファイルのパス
            dtype: 列名とデータ型の辞書
            annotated_cols: アノテーション対象の列名のリスト
        returns:
            AnnotationData: 読み込んだアノテーションデータ
        """
        # str型など，Noneに対応できない型を指定した場合，エラーになるため，先に読み込んでから型変換する
        df = pd.read_excel(file_path)

        # アノテーション対象のデータに欠損値がある場合，エラーを発生させる
        if df[annotated_cols].isnull().any().any():
            raise MissingValueError("アノテーションデータに欠損値が含まれています。")

        df = df.astype(dtype)

        result = AnnotationData(df)
        result.annotated_cols = annotated_cols
        return result
