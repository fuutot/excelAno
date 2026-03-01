import pandas as pd
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


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
            bold_font = Font(bold=True, color="FFFFFF")  # 白いテキスト
            header_fill = PatternFill(start_color="1F4E78", fill_type="solid")  # 濃い青
            for cell in worksheet[1]:
                cell.font = bold_font
                cell.border = thin_border
                cell.fill = header_fill

            # ヘッダー以外には罫線を適用し、行ごとに色を交互に設定
            light_blue_fill = PatternFill(start_color="D9E1F2", fill_type="solid")  # 薄い青
            for row_num, row in enumerate(
                worksheet.iter_rows(min_row=2, max_row=worksheet.max_row, min_col=1, max_col=worksheet.max_column),
                start=2,
            ):
                for cell in row:
                    cell.border = thin_border
                    # 偶数行に薄い青を適用（2,4,6...）
                    if row_num % 2 == 0:
                        cell.fill = light_blue_fill

            # 列の最大文字列長を計算して、文字折り返しが必要な列を判定
            max_char_limit = 20  # この値を超える列に対して文字折り返しを適用

            for col_num, column in enumerate(worksheet.columns, 1):
                max_length = 0
                column_letter = get_column_letter(col_num)

                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except TypeError:
                        pass

                # 文字列が長い列にのみ文字折り返しを適用
                if max_length > max_char_limit:
                    for cell in column:
                        cell.alignment = Alignment(wrap_text=True)
                    # 列幅を適切に設定
                    worksheet.column_dimensions[column_letter].width = 30
                else:
                    # 短い列は自動調整
                    worksheet.column_dimensions[column_letter].width = max_length + 2

            # ヘッダーの行を固定
            worksheet.freeze_panes = "A2"


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
