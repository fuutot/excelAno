import pandas as pd


class Template(pd.DataFrame):
    """アノテーション用のエクセルファイルのテンプレートを作成するためのクラス"""

    @staticmethod
    def from_dataframe(df: pd.DataFrame) -> "Template":
        """
        DataFrameからテンプレートを作成するメソッド
        args:
            df: テンプレートの元となるDataFrame
        returns:
            Template: 作成したテンプレート
        """
        return Template(df)

    @staticmethod
    def from_csv(file_path: str) -> "Template":
        """
        CSVファイルからテンプレートを作成するメソッド
        args:
            file_path: CSVファイルのパス
        returns:
            Template: 作成したテンプレート
        """
        df = pd.read_csv(file_path)
        return Template(df)

    def to_excel(self, file_path: str) -> None:
        """
        テンプレートをエクセルファイルに保存するメソッド
        args:
            file_path: 保存するエクセルファイルのパス
        """
        # TODO: アノテーションファイルに必要な書式設定を追加する
        # 例: セルの背景色を変更する，列幅を調整する,特定の列の値は変化させないなど

        self.to_excel(file_path, index=False)
