import pandas as pd
import pandas.api.types as pd_types
import pytest

from excelano.anotation_data import AnotationData, MissingValueError

SAMPLE_DATA = {
    "query_id": ["query_1", "query_2", "query_3"],
    "document_id": ["doc_1", "doc_2", "doc_3"],
    "query": ["What is AI?", "What is ML?", "What is DL?"],
    "document": [
        "AI is Artificial Intelligence.",
        "ML is Machine Learning.",
        "DL is Deep Learning.",
    ],
    "relevance": [1, 1, 1],
}
SAMPLE_DATA_DTYPE = {
    "query_id": str,
    "document_id": str,
    "query": str,
    "document": str,
    "relevance": int,
}


def test_from_excel_reads_data(tmp_path):
    df = pd.DataFrame(SAMPLE_DATA)
    file_path = tmp_path / "annotations.xlsx"
    df.to_excel(file_path, index=False)

    result = AnotationData.from_excel(
        file_path=str(file_path),
        dtype=SAMPLE_DATA_DTYPE,
        anotated_cols=["relevance"],
    )

    assert isinstance(result, AnotationData)
    assert list(result.columns) == [
        "query_id",
        "document_id",
        "query",
        "document",
        "relevance",
    ]
    assert result["query_id"].tolist() == ["query_1", "query_2", "query_3"]
    assert result["query"].tolist() == ["What is AI?", "What is ML?", "What is DL?"]
    assert result["relevance"].tolist() == [1, 1, 1]
    assert result.anotated_cols == ["relevance"]


def test_from_excel_applies_dtype(tmp_path):
    df = pd.DataFrame(SAMPLE_DATA)
    file_path = tmp_path / "annotations.xlsx"
    df.to_excel(file_path, index=False)

    result = AnotationData.from_excel(
        file_path=str(file_path),
        dtype=SAMPLE_DATA_DTYPE,
        anotated_cols=["relevance"],
    )

    # Python標準の型はpandasのdtypeをうまく判定できないため，pd.api.typesを使う
    assert pd_types.is_string_dtype(result["query_id"])
    assert pd_types.is_string_dtype(result["query"])
    assert pd_types.is_integer_dtype(result["relevance"])


SAMPLE_DATA_INCOMPLETE = {
    "query_id": ["query_1", "query_2", "query_3"],
    "document_id": ["doc_1", "doc_2", "doc_3"],
    "query": ["What is AI?", "What is ML?", "What is DL?"],
    "document": [
        "AI is Artificial Intelligence.",
        "ML is Machine Learning.",
        "DL is Deep Learning.",
    ],
    "relevance": [1, None, 1],  # 2行目のrelevanceがNone（欠損値）になっているデータ
}


def test_from_excel_with_incomplete_data(tmp_path):
    df = pd.DataFrame(SAMPLE_DATA_INCOMPLETE)
    file_path = tmp_path / "annotations_incomplete.xlsx"
    df.to_excel(file_path, index=False)

    # アノテーション対象のデータに欠損値がある場合，エラーを発生させる
    with pytest.raises(
        MissingValueError, match="アノテーションデータに欠損値が含まれています。"
    ):
        AnotationData.from_excel(
            file_path=str(file_path),
            dtype=SAMPLE_DATA_DTYPE,
            anotated_cols=["relevance"],
        )
