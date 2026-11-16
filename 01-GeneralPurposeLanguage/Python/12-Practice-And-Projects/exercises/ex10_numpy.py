"""ex10_numpy - NumPy practice: indexing, broadcasting, masking, reshaping, einsum.

Every function should be vectorized: no Python loops over array elements.
"""
import numpy as np


def corners(a):
    """Return the four corner values of a 2D array as a 1D array:
    [top-left, top-right, bottom-left, bottom-right].

    Example: corners(np.arange(12).reshape(3, 4)) -> [0, 3, 8, 11]
    Level: easy
    Hint: index with two lists of row and column positions at once.
    """
    raise NotImplementedError


def center_columns(a):
    """Subtract each column's mean from that column (mean of every column becomes 0).

    Example: center_columns([[1, 10], [3, 30]]) -> [[-1, -10], [1, 10]]
    Level: easy
    Hint: a.mean(axis=0) has shape (ncols,), which broadcasts across rows.
    """
    raise NotImplementedError


def grade_labels(scores):
    """Turn numeric scores into letters: >= 80 'A', >= 50 'B', otherwise 'C'.
    Return a numpy array of strings with the same shape.

    Example: grade_labels([90, 50, 10]) -> ['A', 'B', 'C']
    Level: easy
    Hint: np.select (or nested np.where) chooses values by condition.
    """
    raise NotImplementedError


def zscore_columns(a):
    """Standardise each column: (value - column mean) / column std (population std, ddof=0).
    A column whose std is 0 must become all zeros (no NaN, no warning).

    Example: zscore_columns([[1, 5], [3, 5]]) -> [[-1, 0], [1, 0]]
    Level: medium
    Hint: replace std==0 by 1 before dividing; the numerator is already 0 there.
    """
    raise NotImplementedError


def replace_outliers(x, k=2.0):
    """Replace every value farther than k standard deviations from the mean
    with the median of the whole array. Return a new float array; do not change x.

    Example: replace_outliers([1, 1, 1, 1, 1, 1, 1, 1, 1, 100], k=2) -> ten values, all 1.0
    Level: medium
    Hint: build a boolean mask, then np.where(mask, median, x).
    """
    raise NotImplementedError


def top_k_indices(x, k):
    """Return the indices of the k largest values, biggest first.
    Ties are broken by the smaller index first.

    Example: top_k_indices([5, 9, 1, 9], 2) -> [1, 3]
    Level: medium
    Hint: argsort the negated array with kind="stable" and slice.
    """
    raise NotImplementedError


def block_sums(a, k):
    """Split a 2D array into non-overlapping k x k blocks and return the sum of each block.
    Both dimensions are divisible by k.

    Example: block_sums(np.ones((4, 4)), 2) -> [[4, 4], [4, 4]]
    Level: medium
    Hint: reshape to (h//k, k, w//k, k) and sum over axes 1 and 3.
    """
    raise NotImplementedError


def rowwise_dot(a, b):
    """For two arrays of shape (n, d) return the dot product of each pair of rows, shape (n,).

    Example: rowwise_dot([[1, 2], [3, 4]], [[1, 1], [2, 0]]) -> [3, 6]
    Level: medium
    Hint: np.einsum("ij,ij->i", a, b)
    """
    raise NotImplementedError


def moving_average(x, w):
    """Return the simple moving average with window w (only full windows).
    The result has length len(x) - w + 1.

    Example: moving_average([1, 2, 3, 4], 2) -> [1.5, 2.5, 3.5]
    Level: medium
    Hint: a cumulative sum lets you get every window sum with one subtraction.
    """
    raise NotImplementedError


def one_hot(labels, n_classes):
    """Return a (len(labels), n_classes) int array with a 1 in each row at the label's column.

    Example: one_hot([0, 2], 3) -> [[1, 0, 0], [0, 0, 1]]
    Level: medium
    Hint: np.eye(n_classes)[labels] or assign with fancy indexing.
    """
    raise NotImplementedError


def pairwise_distances(points):
    """Given points of shape (n, d), return the (n, n) matrix of Euclidean distances.

    Example: pairwise_distances([[0, 0], [3, 4]]) -> [[0, 5], [5, 0]]
    Level: hard
    Hint: points[:, None, :] - points[None, :, :] has shape (n, n, d).
    """
    raise NotImplementedError


def nearest_neighbor(points):
    """For each point return the index of its nearest OTHER point (ties: smaller index).

    Example: nearest_neighbor([[0, 0], [1, 0], [10, 0]]) -> [1, 0, 1]
    Level: hard
    Hint: reuse a distance matrix, set its diagonal to infinity, then argmin along axis 1.
    """
    raise NotImplementedError
