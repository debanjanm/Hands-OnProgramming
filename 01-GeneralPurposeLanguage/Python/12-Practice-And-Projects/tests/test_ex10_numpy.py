import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal


@pytest.fixture(scope="module")
def ex(load):
    return load("ex10_numpy")


# 1 corners
def test_corners_basic(ex):
    assert_array_equal(ex.corners(np.arange(12).reshape(3, 4)), [0, 3, 8, 11])


def test_corners_two_by_two(ex):
    assert_array_equal(ex.corners(np.array([[1, 2], [3, 4]])), [1, 2, 3, 4])


def test_corners_single_row_repeats_values(ex):
    assert_array_equal(ex.corners(np.array([[7, 8, 9]])), [7, 9, 7, 9])


# 2 center_columns
def test_center_columns_example(ex):
    assert_allclose(ex.center_columns(np.array([[1.0, 10], [3, 30]])), [[-1, -10], [1, 10]])


def test_center_columns_means_are_zero(ex):
    a = np.random.default_rng(0).normal(5, 2, size=(20, 4))
    assert_allclose(ex.center_columns(a).mean(axis=0), 0, atol=1e-12)


def test_center_columns_does_not_change_input(ex):
    a = np.array([[1.0, 2], [3, 4]])
    ex.center_columns(a)
    assert_array_equal(a, [[1, 2], [3, 4]])


# 3 grade_labels
def test_grade_labels_example(ex):
    assert_array_equal(ex.grade_labels([90, 50, 10]), ["A", "B", "C"])


def test_grade_labels_boundaries(ex):
    assert_array_equal(ex.grade_labels([80, 79.9, 50, 49.9]), ["A", "B", "B", "C"])


def test_grade_labels_keeps_shape(ex):
    out = ex.grade_labels(np.array([[100, 0], [60, 85]]))
    assert out.shape == (2, 2)
    assert_array_equal(out, [["A", "C"], ["B", "A"]])


# 4 zscore_columns
def test_zscore_example(ex):
    assert_allclose(ex.zscore_columns(np.array([[1, 5], [3, 5]])), [[-1, 0], [1, 0]])


def test_zscore_mean_zero_std_one(ex):
    a = np.random.default_rng(1).uniform(0, 100, size=(50, 3))
    z = ex.zscore_columns(a)
    assert_allclose(z.mean(axis=0), 0, atol=1e-12)
    assert_allclose(z.std(axis=0), 1)


def test_zscore_constant_column_is_zero_without_warning(ex):
    z = ex.zscore_columns(np.full((4, 2), 3.0))
    assert_array_equal(z, np.zeros((4, 2)))


# 5 replace_outliers
def test_replace_outliers_example(ex):
    x = np.array([1] * 9 + [100])
    assert_allclose(ex.replace_outliers(x, k=2), np.ones(10))


def test_replace_outliers_nothing_to_replace(ex):
    x = np.array([1.0, 2, 3, 4, 5])
    assert_allclose(ex.replace_outliers(x, k=3), x)


def test_replace_outliers_uses_overall_median_and_keeps_input(ex):
    x = np.array([1.0, 2, 3, 4, 5, 2, 3, 4, 3, 1000])
    out = ex.replace_outliers(x, k=2)
    assert out[-1] == np.median(x)
    assert x[-1] == 1000
    assert_allclose(out[:-1], x[:-1])


# 6 top_k_indices
def test_top_k_example(ex):
    assert_array_equal(ex.top_k_indices([5, 9, 1, 9], 2), [1, 3])


def test_top_k_descending_order(ex):
    assert_array_equal(ex.top_k_indices(np.array([3, 8, 1, 6, 4]), 3), [1, 3, 4])


def test_top_k_zero_and_all(ex):
    assert len(ex.top_k_indices([1, 2, 3], 0)) == 0
    assert_array_equal(ex.top_k_indices([1, 3, 2], 3), [1, 2, 0])


def test_top_k_negative_values(ex):
    assert_array_equal(ex.top_k_indices([-5, -1, -3], 1), [1])


# 7 block_sums
def test_block_sums_ones(ex):
    assert_array_equal(ex.block_sums(np.ones((4, 4)), 2), np.full((2, 2), 4.0))


def test_block_sums_arange(ex):
    a = np.arange(16).reshape(4, 4)
    assert_array_equal(ex.block_sums(a, 2), [[10, 18], [42, 50]])


def test_block_sums_k_equals_size_and_k_one(ex):
    a = np.arange(6).reshape(2, 3)
    assert_array_equal(ex.block_sums(a, 1), a)
    assert_array_equal(ex.block_sums(np.arange(4).reshape(2, 2), 2), [[6]])


def test_block_sums_rectangular(ex):
    a = np.ones((2, 6))
    assert_array_equal(ex.block_sums(a, 2), [[4, 4, 4]])


# 8 rowwise_dot
def test_rowwise_dot_example(ex):
    assert_allclose(ex.rowwise_dot(np.array([[1, 2], [3, 4]]), np.array([[1, 1], [2, 0]])), [3, 6])


def test_rowwise_dot_matches_loop(ex):
    rng = np.random.default_rng(2)
    a, b = rng.normal(size=(5, 3)), rng.normal(size=(5, 3))
    expected = [np.dot(x, y) for x, y in zip(a, b)]
    assert_allclose(ex.rowwise_dot(a, b), expected)


def test_rowwise_dot_orthogonal_rows(ex):
    assert_allclose(ex.rowwise_dot(np.array([[1, 0]]), np.array([[0, 1]])), [0])


# 9 moving_average
def test_moving_average_example(ex):
    assert_allclose(ex.moving_average([1, 2, 3, 4], 2), [1.5, 2.5, 3.5])


def test_moving_average_window_one_is_identity(ex):
    assert_allclose(ex.moving_average([4, 5, 6], 1), [4, 5, 6])


def test_moving_average_full_window(ex):
    assert_allclose(ex.moving_average([2, 4, 6], 3), [4])


def test_moving_average_length(ex):
    assert len(ex.moving_average(np.arange(10), 4)) == 7


# 10 one_hot
def test_one_hot_example(ex):
    assert_array_equal(ex.one_hot([0, 2], 3), [[1, 0, 0], [0, 0, 1]])


def test_one_hot_rows_sum_to_one(ex):
    out = ex.one_hot(np.array([1, 1, 0, 3]), 4)
    assert out.shape == (4, 4)
    assert_array_equal(out.sum(axis=1), 1)
    assert_array_equal(out.argmax(axis=1), [1, 1, 0, 3])


def test_one_hot_empty(ex):
    assert ex.one_hot([], 3).shape == (0, 3)


# 11 pairwise_distances
def test_pairwise_distances_3_4_5(ex):
    assert_allclose(ex.pairwise_distances([[0, 0], [3, 4]]), [[0, 5], [5, 0]])


def test_pairwise_distances_symmetric_zero_diagonal(ex):
    p = np.random.default_rng(3).normal(size=(6, 3))
    d = ex.pairwise_distances(p)
    assert d.shape == (6, 6)
    assert_allclose(d, d.T)
    assert_allclose(np.diag(d), 0)


def test_pairwise_distances_one_point(ex):
    assert_allclose(ex.pairwise_distances([[1.0, 2.0]]), [[0.0]])


def test_pairwise_distances_one_dimension(ex):
    assert_allclose(ex.pairwise_distances([[0], [2], [7]]), [[0, 2, 7], [2, 0, 5], [7, 5, 0]])


# 12 nearest_neighbor
def test_nearest_neighbor_example(ex):
    assert_array_equal(ex.nearest_neighbor([[0, 0], [1, 0], [10, 0]]), [1, 0, 1])


def test_nearest_neighbor_never_itself(ex):
    p = np.random.default_rng(4).normal(size=(10, 2))
    nn = ex.nearest_neighbor(p)
    assert (nn != np.arange(10)).all()


def test_nearest_neighbor_tie_picks_smaller_index(ex):
    assert_array_equal(ex.nearest_neighbor([[0.0], [-1.0], [1.0]])[0], 1)


def test_nearest_neighbor_two_points(ex):
    assert_array_equal(ex.nearest_neighbor([[0, 0], [5, 5]]), [1, 0])


@pytest.mark.parametrize("dtype", [np.uint8, np.uint64, np.int8])
def test_top_k_indices_handles_integer_limits_and_ties(ex, dtype):
    values = np.array([0, 5, 9, 9], dtype=dtype)
    assert_array_equal(ex.top_k_indices(values, 3), [2, 3, 1])


def test_top_k_indices_handles_minimum_signed_integer(ex):
    assert_array_equal(ex.top_k_indices(np.array([-128, 0, 127], dtype=np.int8), 2), [2, 1])
