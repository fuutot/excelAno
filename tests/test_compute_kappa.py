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


def _make_annotation_data(data: dict, annotated_col: str, id_cols: list[str]) -> AnnotationData:
    """テスト用のAnnotationDataを作成するヘルパー関数"""
    import pandas as pd

    df = pd.DataFrame(data)
    result = AnnotationData(df)
    result.annotated_cols = [annotated_col]
    result.id_cols = sorted(id_cols)
    return result


class TestCohenKappaForTwoAnnotators:
    """2評価者のときにCohen's kappaが正しく計算されることを確認するテスト"""

    def test_perfect_agreement_returns_one(self):
        """2評価者が完全に一致しているとき，kappa = 1.0 になることを確認する"""
        annotator_a = _make_annotation_data(PERFECT_AGREEMENT_ANNOTATOR_A, "relevance", id_cols=["query_id"])
        annotator_b = _make_annotation_data(PERFECT_AGREEMENT_ANNOTATOR_B, "relevance", id_cols=["query_id"])
        multi = MultipleAnnotationData([annotator_a, annotator_b])

        kappa = multi.compute_kappa("relevance")

        assert kappa == pytest.approx(1.0)

    def test_no_agreement_returns_negative_one(self):
        """2評価者が全く一致しないとき，kappa = -1.0 になることを確認する"""
        annotator_a = _make_annotation_data(NO_AGREEMENT_ANNOTATOR_A, "relevance", id_cols=["query_id"])
        annotator_b = _make_annotation_data(NO_AGREEMENT_ANNOTATOR_B, "relevance", id_cols=["query_id"])
        multi = MultipleAnnotationData([annotator_a, annotator_b])

        kappa = multi.compute_kappa("relevance")

        assert kappa == pytest.approx(-1.0)

    def test_partial_agreement_returns_value_between_minus_one_and_one(self):
        """2評価者が部分的に一致しているとき，kappaが-1〜1の範囲に収まることを確認する"""

        # 4件中3件一致（q1, q2, q3 は一致, q4 は不一致）
        annotator_a = _make_annotation_data(
            {"query_id": ["q1", "q2", "q3", "q4"], "relevance": [1, 1, 0, 0]}, "relevance", id_cols=["query_id"]
        )
        annotator_b = _make_annotation_data(
            {"query_id": ["q1", "q2", "q3", "q4"], "relevance": [1, 1, 0, 1]}, "relevance", id_cols=["query_id"]
        )
        multi = MultipleAnnotationData([annotator_a, annotator_b])

        kappa = multi.compute_kappa("relevance")

        assert -1.0 <= kappa <= 1.0


class TestFleissKappaForThreeOrMoreAnnotators:
    """3評価者以上のときにFleiss' kappaが正しく計算されることを確認するテスト"""

    def test_perfect_agreement_with_three_annotators_returns_one(self):
        """3評価者が完全に一致しているとき，kappa = 1.0 になることを確認する"""
        annotator_a = _make_annotation_data(PERFECT_AGREEMENT_ANNOTATOR_A, "relevance", id_cols=["query_id"])
        annotator_b = _make_annotation_data(PERFECT_AGREEMENT_ANNOTATOR_B, "relevance", id_cols=["query_id"])
        annotator_c = _make_annotation_data(PERFECT_AGREEMENT_ANNOTATOR_A, "relevance", id_cols=["query_id"])
        multi = MultipleAnnotationData([annotator_a, annotator_b, annotator_c])

        kappa = multi.compute_kappa("relevance")

        assert kappa == pytest.approx(1.0)

    def test_three_annotators_returns_value_between_minus_one_and_one(self):
        """3評価者の場合，kappaが-1〜1の範囲に収まることを確認する"""
        annotator_a = _make_annotation_data(FLEISS_EXAMPLE_ANNOTATOR_A, "category", id_cols=["query_id"])
        annotator_b = _make_annotation_data(FLEISS_EXAMPLE_ANNOTATOR_B, "category", id_cols=["query_id"])
        annotator_c = _make_annotation_data(FLEISS_EXAMPLE_ANNOTATOR_C, "category", id_cols=["query_id"])
        multi = MultipleAnnotationData([annotator_a, annotator_b, annotator_c])

        kappa = multi.compute_kappa("category")

        assert -1.0 <= kappa <= 1.0

    def test_four_annotators_uses_fleiss_kappa(self):
        """4評価者でもFleiss' kappaが正しく計算されることを確認する"""
        annotator_a = _make_annotation_data(PERFECT_AGREEMENT_ANNOTATOR_A, "relevance", id_cols=["query_id"])
        annotator_b = _make_annotation_data(PERFECT_AGREEMENT_ANNOTATOR_B, "relevance", id_cols=["query_id"])
        annotator_c = _make_annotation_data(PERFECT_AGREEMENT_ANNOTATOR_A, "relevance", id_cols=["query_id"])
        annotator_d = _make_annotation_data(PERFECT_AGREEMENT_ANNOTATOR_B, "relevance", id_cols=["query_id"])
        multi = MultipleAnnotationData([annotator_a, annotator_b, annotator_c, annotator_d])

        kappa = multi.compute_kappa("relevance")

        assert kappa == pytest.approx(1.0)

    def test_known_fleiss_kappa_value(self):
        """既知のデータで計算されるFleiss' kappaの値が期待値と一致することを確認する

        3評価者，5アイテム，各評価者の評価:
        A: [1,1,2,2,3], B: [1,2,2,3,3], C: [1,1,2,2,3]
        手動計算による期待kappa ≈ 0.595
        """
        annotator_a = _make_annotation_data(FLEISS_EXAMPLE_ANNOTATOR_A, "category", id_cols=["query_id"])
        annotator_b = _make_annotation_data(FLEISS_EXAMPLE_ANNOTATOR_B, "category", id_cols=["query_id"])
        annotator_c = _make_annotation_data(FLEISS_EXAMPLE_ANNOTATOR_C, "category", id_cols=["query_id"])
        multi = MultipleAnnotationData([annotator_a, annotator_b, annotator_c])

        kappa = multi.compute_kappa("category")

        assert kappa == pytest.approx(0.595, abs=0.01)


class TestAnnotationTargetAlignment:
    """評価対象の照合（ID整列・不一致検出）に関するテスト"""

    def test_different_row_order_produces_same_kappa_as_aligned_order(self):
        """行順が異なる2評価者のデータでも，IDで整列することで同じkappa値が得られることを確認する"""
        # annotator_b のデータは行順が逆になっているが，query_id で整列されるため同じ結果になるはず
        annotator_a = _make_annotation_data(
            {"query_id": ["q1", "q2", "q3", "q4"], "relevance": [1, 0, 1, 0]}, "relevance", id_cols=["query_id"]
        )
        annotator_b_reversed = _make_annotation_data(
            {"query_id": ["q4", "q3", "q2", "q1"], "relevance": [0, 1, 0, 1]}, "relevance", id_cols=["query_id"]
        )
        annotator_b_aligned = _make_annotation_data(
            {"query_id": ["q1", "q2", "q3", "q4"], "relevance": [1, 0, 1, 0]}, "relevance", id_cols=["query_id"]
        )

        kappa_reversed = MultipleAnnotationData([annotator_a, annotator_b_reversed]).compute_kappa("relevance")
        kappa_aligned = MultipleAnnotationData([annotator_a, annotator_b_aligned]).compute_kappa("relevance")

        assert kappa_reversed == pytest.approx(kappa_aligned)

    def test_mismatched_evaluation_targets_raise_error(self):
        """評価者間で評価対象が異なる場合にエラーが発生することを確認する"""
        annotator_a = _make_annotation_data(
            {"query_id": ["q1", "q2", "q3"], "relevance": [1, 0, 1]}, "relevance", id_cols=["query_id"]
        )
        # annotator_b は q3 の代わりに q4 を評価している
        annotator_b_different_items = _make_annotation_data(
            {"query_id": ["q1", "q2", "q4"], "relevance": [1, 0, 1]}, "relevance", id_cols=["query_id"]
        )

        with pytest.raises(
            AnnotationTargetMismatchError,
            match="すべてのAnnotationDataが同じ評価対象を持っている必要があります。すべてのAnnotationDataが同じ評価対象に対してアノテーションを行っていることを確認してください。",
        ):
            MultipleAnnotationData([annotator_a, annotator_b_different_items]).compute_kappa("relevance")


class TestMultipleIdColumns:
    """id_colsが複数の要素からなる場合のテスト"""

    def test_two_id_columns_perfect_agreement(self):
        """query_idとdoc_idの2つのIDカラムで完全一致する場合，kappa = 1.0 になることを確認する"""
        annotator_a = _make_annotation_data(
            {
                "query_id": ["q1", "q1", "q2", "q2"],
                "doc_id": ["d1", "d2", "d1", "d2"],
                "relevance": [1, 0, 1, 0],
            },
            "relevance",
            id_cols=["query_id", "doc_id"],
        )
        annotator_b = _make_annotation_data(
            {
                "query_id": ["q1", "q1", "q2", "q2"],
                "doc_id": ["d1", "d2", "d1", "d2"],
                "relevance": [1, 0, 1, 0],
            },
            "relevance",
            id_cols=["query_id", "doc_id"],
        )
        multi = MultipleAnnotationData([annotator_a, annotator_b])

        kappa = multi.compute_kappa("relevance")

        assert kappa == pytest.approx(1.0)

    def test_two_id_columns_different_row_order(self):
        """複数IDカラムで行順が異なる場合でも正しく整列されることを確認する"""
        annotator_a = _make_annotation_data(
            {
                "query_id": ["q1", "q1", "q2", "q2"],
                "doc_id": ["d1", "d2", "d1", "d2"],
                "relevance": [1, 0, 1, 0],
            },
            "relevance",
            id_cols=["query_id", "doc_id"],
        )
        # annotator_b は行順が異なる
        annotator_b = _make_annotation_data(
            {
                "query_id": ["q2", "q1", "q2", "q1"],
                "doc_id": ["d2", "d1", "d1", "d2"],
                "relevance": [0, 1, 1, 0],
            },
            "relevance",
            id_cols=["query_id", "doc_id"],
        )
        multi = MultipleAnnotationData([annotator_a, annotator_b])

        kappa = multi.compute_kappa("relevance")

        assert kappa == pytest.approx(1.0)

    def test_two_id_columns_mismatched_targets_raise_error(self):
        """複数IDカラムで評価対象が異なる場合にエラーが発生することを確認する"""
        annotator_a = _make_annotation_data(
            {
                "query_id": ["q1", "q1", "q2"],
                "doc_id": ["d1", "d2", "d1"],
                "relevance": [1, 0, 1],
            },
            "relevance",
            id_cols=["query_id", "doc_id"],
        )
        # annotator_b は (q2, d2) の代わりに (q2, d3) を評価している
        annotator_b = _make_annotation_data(
            {
                "query_id": ["q1", "q1", "q2"],
                "doc_id": ["d1", "d2", "d3"],
                "relevance": [1, 0, 1],
            },
            "relevance",
            id_cols=["query_id", "doc_id"],
        )

        with pytest.raises(
            AnnotationTargetMismatchError,
            match="すべてのAnnotationDataが同じ評価対象を持っている必要があります。すべてのAnnotationDataが同じ評価対象に対してアノテーションを行っていることを確認してください。",
        ):
            MultipleAnnotationData([annotator_a, annotator_b])

    def test_three_id_columns_with_three_annotators(self):
        """3つのIDカラムと3評価者でFleiss' kappaが正しく計算されることを確認する"""
        annotator_a = _make_annotation_data(
            {
                "query_id": ["q1", "q1", "q2", "q2"],
                "doc_id": ["d1", "d1", "d2", "d2"],
                "aspect": ["a1", "a2", "a1", "a2"],
                "rating": [1, 1, 0, 0],
            },
            "rating",
            id_cols=["query_id", "doc_id", "aspect"],
        )
        annotator_b = _make_annotation_data(
            {
                "query_id": ["q1", "q1", "q2", "q2"],
                "doc_id": ["d1", "d1", "d2", "d2"],
                "aspect": ["a1", "a2", "a1", "a2"],
                "rating": [1, 1, 0, 0],
            },
            "rating",
            id_cols=["query_id", "doc_id", "aspect"],
        )
        annotator_c = _make_annotation_data(
            {
                "query_id": ["q1", "q1", "q2", "q2"],
                "doc_id": ["d1", "d1", "d2", "d2"],
                "aspect": ["a1", "a2", "a1", "a2"],
                "rating": [1, 1, 0, 0],
            },
            "rating",
            id_cols=["query_id", "doc_id", "aspect"],
        )
        multi = MultipleAnnotationData([annotator_a, annotator_b, annotator_c])

        kappa = multi.compute_kappa("rating")

        assert kappa == pytest.approx(1.0)

    def test_different_id_cols_order_auto_align(self):
        """id_colsの順序が異なる場合でも，kappa係数を計算する"""
        annotator_a = _make_annotation_data(
            {
                "query_id": ["q1", "q2"],
                "doc_id": ["d1", "d2"],
                "relevance": [1, 0],
            },
            "relevance",
            id_cols=["query_id", "doc_id"],
        )
        # annotator_bのid_colsの順序が異なるが、自動で合わせられるべき
        annotator_b = _make_annotation_data(
            {
                "query_id": ["q1", "q2"],
                "doc_id": ["d1", "d2"],
                "relevance": [1, 0],
            },
            "relevance",
            id_cols=["doc_id", "query_id"],
        )

        multi = MultipleAnnotationData([annotator_a, annotator_b])
        kappa = multi.compute_kappa("relevance")

        # id_colsの順序が異なっていても、自動で整列されて完全一致するためkappa = 1.0
        assert kappa == pytest.approx(1.0)


class TestRealData:
    """実際のデータでkappaが計算できることを確認するテスト"""

    def test_fleiss_kappa(self):
        """
        実際のデータでFleiss' kappaが計算できることを確認する
        データソース： https://en.wikipedia.org/wiki/Fleiss%27s_kappa
        """
        ratings = [
            [5, 2, 3, 2, 1, 1, 1, 1, 1, 2],
            [5, 2, 3, 2, 1, 1, 1, 1, 1, 2],
            [5, 3, 3, 2, 2, 1, 1, 2, 1, 3],
            [5, 3, 4, 3, 2, 1, 2, 2, 1, 3],
            [5, 3, 4, 3, 3, 1, 2, 2, 1, 4],
            [5, 3, 4, 3, 3, 1, 3, 2, 1, 4],
            [5, 3, 4, 3, 3, 1, 3, 2, 3, 4],
            [5, 3, 4, 3, 3, 2, 3, 3, 2, 5],
            [5, 4, 5, 3, 3, 2, 3, 3, 2, 5],
            [5, 4, 5, 3, 3, 2, 3, 3, 2, 5],
            [5, 4, 5, 3, 3, 2, 3, 4, 2, 5],
            [5, 4, 5, 3, 3, 2, 4, 4, 2, 5],
            [5, 5, 5, 4, 4, 2, 4, 5, 3, 5],
            [5, 5, 5, 4, 5, 2, 4, 5, 4, 5],
        ]

        # ratingsがソースとなっている表と一致するのか確認
        annotator = 14
        assert len(ratings) == annotator

        num_items = 10
        assert all(len(rating) == num_items for rating in ratings)

        real_data = [
            [0, 0, 0, 0, 14],  # item 1
            [0, 2, 6, 4, 2],  # item 2
            [0, 0, 3, 5, 6],  # item 3
            [0, 3, 9, 2, 0],  # item 4
            [2, 2, 8, 1, 1],  # item 5
            [7, 7, 0, 0, 0],  # item 6
            [3, 2, 6, 3, 0],  # item 7
            [2, 5, 3, 2, 2],  # item 8
            [6, 5, 2, 1, 0],  # item 9
            [0, 2, 2, 3, 7],  # item 10
        ]

        expected_counts = [[0, 0, 0, 0, 0] for _ in range(num_items)]
        for annotator_i in range(len(ratings)):
            for item_j in range(len(ratings[annotator_i])):
                rating = ratings[annotator_i][item_j]
                expected_counts[item_j][rating - 1] += 1

        assert expected_counts == real_data

        # fleiss_kappaの計算
        kappa = MultipleAnnotationData._compute_fleiss_kappa(ratings)
        kappa_ans = 0.210
        assert kappa == pytest.approx(kappa_ans, abs=0.001)
