import pandas as pd
from openpyxl.styles import Border, Font, Side


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

            worksheet = writer.sheets["Sheet1"]

            # 罫線のスタイルを定義
            thin_border = Border(
                left=Side(style="thin"),
                right=Side(style="thin"),
                top=Side(style="thin"),
                bottom=Side(style="thin"),
            )

            # ヘッダーの書式を設定
            bold_font = Font(bold=True)
            for cell in worksheet[1]:
                cell.font = bold_font
                cell.border = thin_border

            # ヘッダー以外には罫線を適用
            for row in worksheet.iter_rows(
                min_row=2, max_row=worksheet.max_row, min_col=1, max_col=worksheet.max_column
            ):
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
