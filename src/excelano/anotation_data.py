import pandas as pd


class MissingValueError(ValueError):
    """アノテーションデータに欠損値が含まれている場合に発生するエラー"""

    pass


class AnotationData(pd.DataFrame):
    @staticmethod
    def from_excel(
        file_path, dtype: dict[str, type], anotated_cols: list[str]
    ) -> "AnotationData":
        """
        エクセル形式のアノテーションデータを読み込むメソッド
        args:
            file_path: エクセルファイルのパス
            dtype: 列名とデータ型の辞書
            anotated_cols: アノテーション対象の列名のリスト
        returns:
            AnotationData: 読み込んだアノテーションデータ
        """
        # str型など，Noneに対応できない型を指定した場合，エラーになるため，先に読み込んでから型変換する
        df = pd.read_excel(file_path)

        # アノテーション対象のデータに欠損値がある場合，エラーを発生させる
        if df[anotated_cols].isnull().any().any():
            raise MissingValueError("アノテーションデータに欠損値が含まれています。")

        df = df.astype(dtype)

        return AnotationData(df)
