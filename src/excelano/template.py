import pandas as pd
from openpyxl.styles import Border, Side


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
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            # DataFrameをエクセルファイルに書き込む
            super().to_excel(writer, index=False)

            # 罫線のスタイルを定義
            thin_border = Border(
                left=Side(style="thin"),
                right=Side(style="thin"),
                top=Side(style="thin"),
                bottom=Side(style="thin"),
            )

            # シートを取得して、すべてのセルに罫線を適用
            worksheet = writer.sheets["Sheet1"]
            for row in worksheet.iter_rows():
                for cell in row:
                    cell.border = thin_border


if __name__ == "__main__":  # テンプレートの作成例
    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "text": ["This is a sample text.", "Another example.", "More data."],
            "label": ["", "", ""],
        }
    )
    template = Template.from_dataframe(df)
    template.to_excel("output/annotation_template.xlsx")
