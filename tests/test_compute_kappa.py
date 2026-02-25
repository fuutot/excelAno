import pytest

from excelano.annotation_data import AnnotationData, AnnotationTargetMismatchError, MultipleAnnotationData

# 2評価者が完全に一致しているデータ（kappa = 1.0 になるはず）
PERFECT_AGREEMENT_ANNOTATOR_A = {
    "query_id": ["q1", "q2", "q3", "q4"],
    "relevance": [1, 0, 1, 0],
}
PERFECT_AGREEMENT_ANNOTATOR_B = {
    "query_id": ["q1", "q2", "q3", "q4"],
    "relevance": [1, 0, 1, 0],
}

# 2評価者が全く一致しないデータ（kappa = -1.0 になるはず）
NO_AGREEMENT_ANNOTATOR_A = {
    "query_id": ["q1", "q2", "q3", "q4"],
    "relevance": [1, 1, 0, 0],
}
NO_AGREEMENT_ANNOTATOR_B = {
    "query_id": ["q1", "q2", "q3", "q4"],
    "relevance": [0, 0, 1, 1],
}

# 3評価者による既知のkappa値を持つデータ（期待kappa ≈ 0.595）
FLEISS_EXAMPLE_ANNOTATOR_A = {
    "query_id": ["q1", "q2", "q3", "q4", "q5"],
    "category": [1, 1, 2, 2, 3],
}
FLEISS_EXAMPLE_ANNOTATOR_B = {
    "query_id": ["q1", "q2", "q3", "q4", "q5"],
    "category": [1, 2, 2, 3, 3],
}
FLEISS_EXAMPLE_ANNOTATOR_C = {
    "query_id": ["q1", "q2", "q3", "q4", "q5"],
    "category": [1, 1, 2, 2, 3],
}


def _make_annotation_data(data: dict, annotated_col: str, id_cols: list[str] | None = None) -> AnnotationData:
    """テスト用のAnnotationDataを作成するヘルパー関数"""
    import pandas as pd

    df = pd.DataFrame(data)
    result = AnnotationData(df)
    result.annotated_cols = [annotated_col]
    result.id_cols = id_cols or []
    return result


class TestCohenKappaForTwoAnnotators:
    """2評価者のときにCohen's kappaが正しく計算されることを確認するテスト"""

    def test_perfect_agreement_returns_one(self):
        """2評価者が完全に一致しているとき，kappa = 1.0 になることを確認する"""
        annotator_a = _make_annotation_data(PERFECT_AGREEMENT_ANNOTATOR_A, "relevance")
        annotator_b = _make_annotation_data(PERFECT_AGREEMENT_ANNOTATOR_B, "relevance")
        multi = MultipleAnnotationData([annotator_a, annotator_b], id_cols=["query_id"])

        kappa = multi.compute_kappa("relevance")

        assert kappa == pytest.approx(1.0)

    def test_no_agreement_returns_negative_one(self):
        """2評価者が全く一致しないとき，kappa = -1.0 になることを確認する"""
        annotator_a = _make_annotation_data(NO_AGREEMENT_ANNOTATOR_A, "relevance")
        annotator_b = _make_annotation_data(NO_AGREEMENT_ANNOTATOR_B, "relevance")
        multi = MultipleAnnotationData([annotator_a, annotator_b], id_cols=["query_id"])

        kappa = multi.compute_kappa("relevance")

        assert kappa == pytest.approx(-1.0)

    def test_partial_agreement_returns_value_between_minus_one_and_one(self):
        """2評価者が部分的に一致しているとき，kappaが-1〜1の範囲に収まることを確認する"""
        import pandas as pd

        # 4件中3件一致（q1, q2, q3 は一致, q4 は不一致）
        annotator_a = _make_annotation_data({"query_id": ["q1", "q2", "q3", "q4"], "relevance": [1, 1, 0, 0]}, "relevance")
        annotator_b = _make_annotation_data({"query_id": ["q1", "q2", "q3", "q4"], "relevance": [1, 1, 0, 1]}, "relevance")
        multi = MultipleAnnotationData([annotator_a, annotator_b], id_cols=["query_id"])

        kappa = multi.compute_kappa("relevance")

        assert -1.0 <= kappa <= 1.0


class TestFleissKappaForThreeOrMoreAnnotators:
    """3評価者以上のときにFleiss' kappaが正しく計算されることを確認するテスト"""

    def test_perfect_agreement_with_three_annotators_returns_one(self):
        """3評価者が完全に一致しているとき，kappa = 1.0 になることを確認する"""
        annotator_a = _make_annotation_data(PERFECT_AGREEMENT_ANNOTATOR_A, "relevance")
        annotator_b = _make_annotation_data(PERFECT_AGREEMENT_ANNOTATOR_B, "relevance")
        annotator_c = _make_annotation_data(PERFECT_AGREEMENT_ANNOTATOR_A, "relevance")
        multi = MultipleAnnotationData([annotator_a, annotator_b, annotator_c], id_cols=["query_id"])

        kappa = multi.compute_kappa("relevance")

        assert kappa == pytest.approx(1.0)

    def test_three_annotators_returns_value_between_minus_one_and_one(self):
        """3評価者の場合，kappaが-1〜1の範囲に収まることを確認する"""
        annotator_a = _make_annotation_data(FLEISS_EXAMPLE_ANNOTATOR_A, "category")
        annotator_b = _make_annotation_data(FLEISS_EXAMPLE_ANNOTATOR_B, "category")
        annotator_c = _make_annotation_data(FLEISS_EXAMPLE_ANNOTATOR_C, "category")
        multi = MultipleAnnotationData([annotator_a, annotator_b, annotator_c], id_cols=["query_id"])

        kappa = multi.compute_kappa("category")

        assert -1.0 <= kappa <= 1.0

    def test_four_annotators_uses_fleiss_kappa(self):
        """4評価者でもFleiss' kappaが正しく計算されることを確認する"""
        annotator_a = _make_annotation_data(PERFECT_AGREEMENT_ANNOTATOR_A, "relevance")
        annotator_b = _make_annotation_data(PERFECT_AGREEMENT_ANNOTATOR_B, "relevance")
        annotator_c = _make_annotation_data(PERFECT_AGREEMENT_ANNOTATOR_A, "relevance")
        annotator_d = _make_annotation_data(PERFECT_AGREEMENT_ANNOTATOR_B, "relevance")
        multi = MultipleAnnotationData([annotator_a, annotator_b, annotator_c, annotator_d], id_cols=["query_id"])

        kappa = multi.compute_kappa("relevance")

        assert kappa == pytest.approx(1.0)

    def test_known_fleiss_kappa_value(self):
        """既知のデータで計算されるFleiss' kappaの値が期待値と一致することを確認する

        3評価者，5アイテム，各評価者の評価:
        A: [1,1,2,2,3], B: [1,2,2,3,3], C: [1,1,2,2,3]
        手動計算による期待kappa ≈ 0.595
        """
        annotator_a = _make_annotation_data(FLEISS_EXAMPLE_ANNOTATOR_A, "category")
        annotator_b = _make_annotation_data(FLEISS_EXAMPLE_ANNOTATOR_B, "category")
        annotator_c = _make_annotation_data(FLEISS_EXAMPLE_ANNOTATOR_C, "category")
        multi = MultipleAnnotationData([annotator_a, annotator_b, annotator_c], id_cols=["query_id"])

        kappa = multi.compute_kappa("category")

        assert kappa == pytest.approx(0.595, abs=0.01)


class TestAnnotationTargetAlignment:
    """評価対象の照合（ID整列・不一致検出）に関するテスト"""

    def test_different_row_order_produces_same_kappa_as_aligned_order(self):
        """行順が異なる2評価者のデータでも，IDで整列することで同じkappa値が得られることを確認する"""
        # annotator_b のデータは行順が逆になっているが，query_id で整列されるため同じ結果になるはず
        annotator_a = _make_annotation_data(
            {"query_id": ["q1", "q2", "q3", "q4"], "relevance": [1, 0, 1, 0]}, "relevance"
        )
        annotator_b_reversed = _make_annotation_data(
            {"query_id": ["q4", "q3", "q2", "q1"], "relevance": [0, 1, 0, 1]}, "relevance"
        )
        annotator_b_aligned = _make_annotation_data(
            {"query_id": ["q1", "q2", "q3", "q4"], "relevance": [1, 0, 1, 0]}, "relevance"
        )

        kappa_reversed = MultipleAnnotationData([annotator_a, annotator_b_reversed], id_cols=["query_id"]).compute_kappa("relevance")
        kappa_aligned = MultipleAnnotationData([annotator_a, annotator_b_aligned], id_cols=["query_id"]).compute_kappa("relevance")

        assert kappa_reversed == pytest.approx(kappa_aligned)

    def test_mismatched_evaluation_targets_raise_error(self):
        """評価者間で評価対象が異なる場合にエラーが発生することを確認する"""
        annotator_a = _make_annotation_data(
            {"query_id": ["q1", "q2", "q3"], "relevance": [1, 0, 1]}, "relevance"
        )
        # annotator_b は q3 の代わりに q4 を評価している
        annotator_b_different_items = _make_annotation_data(
            {"query_id": ["q1", "q2", "q4"], "relevance": [1, 0, 1]}, "relevance"
        )

        with pytest.raises(AnnotationTargetMismatchError, match="評価対象が一致しません"):
            MultipleAnnotationData([annotator_a, annotator_b_different_items], id_cols=["query_id"]).compute_kappa("relevance")
