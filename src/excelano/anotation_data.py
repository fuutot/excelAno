import pandas as pd


class AnotationData(pd.DataFrame):
    @staticmethod
    def from_excel(file_path, dtype: dict[str, type]) -> "AnotationData":
        """
        エクセル形式のアノテーションデータを読み込むメソッド
        args:
            file_path: エクセルファイルのパス
            dtype: 列名とデータ型の辞書
        returns:
            AnotationData: 読み込んだアノテーションデータ
        """
        df = pd.read_excel(file_path, dtype=dtype)
        return AnotationData(df)
