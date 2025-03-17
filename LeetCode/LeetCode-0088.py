"""
LeetCode 88: Merge Sorted Array

1. Problem Statement:
You are given two integer arrays nums1 and nums2, sorted in non-decreasing order, and two integers m and n, representing the number of elements in nums1 and nums2 respectively.

Merge nums1 and nums2 into a single array sorted in non-decreasing order.

The final sorted array should not be returned by the function, but instead be stored inside the array nums1. To accommodate this, nums1 has a length of m + n, where the first m elements denote the elements that should be merged, and the last n elements are set to 0 and should be ignored. nums2 has a length of n.

2. Code Implementation:
"""

def merge(nums1, m, nums2, n):
    """
    Merge nums1 and nums2 into a single array sorted in non-decreasing order.
    
    Args:
        nums1 (List[int]): First sorted array with extra space at the end
        m (int): Number of elements in nums1
        nums2 (List[int]): Second sorted array
        n (int): Number of elements in nums2
        
    Returns:
        None: nums1 is modified in-place
    """
    # Initialize pointers for nums1, nums2, and the position to fill in nums1
    p1 = m - 1  # Pointer for the last element in the original nums1
    p2 = n - 1  # Pointer for the last element in nums2
    p = m + n - 1  # Pointer for the last position in merged nums1
    
    # Merge from the end to the beginning
    while p1 >= 0 and p2 >= 0:
        if nums1[p1] > nums2[p2]:
            nums1[p] = nums1[p1]
            p1 -= 1
        else:
            nums1[p] = nums2[p2]
            p2 -= 1
        p -= 1
    
    # If there are remaining elements in nums2, copy them to nums1
    # (No need to handle remaining elements in nums1, they're already in place)
    while p2 >= 0:
        nums1[p] = nums2[p2]
        p2 -= 1
        p -= 1

"""
3. Pattern Name:
Two Pointers / Merge Operation

4. Explanation:
This problem asks us to merge two sorted arrays into the first array, which has enough space at the end to accommodate all elements.

The key insight is to merge from the end rather than the beginning. Here's why:
- If we merge from the beginning, we risk overwriting elements in nums1 that we haven't processed yet
- By merging from the end, we fill the largest empty spaces first, avoiding any conflicts

The approach:
1. Initialize three pointers:
   - p1: Points to the last real element in nums1
   - p2: Points to the last element in nums2
   - p: Points to the last position in the merged array (end of nums1)

2. Compare elements from the end of both arrays:
   - If nums1[p1] > nums2[p2], place nums1[p1] at position p and decrement p1
   - Otherwise, place nums2[p2] at position p and decrement p2
   - Decrement p after each placement

3. After the main loop, if there are remaining elements in nums2, copy them to nums1
   - Note: We don't need to handle remaining elements in nums1 because they're already in their correct positions

This approach ensures that:
- We never overwrite elements we still need
- We maintain the sorted order
- We use the existing space in nums1

5. Complexity Analysis:
Time Complexity: O(m + n)
- We process each element in both arrays exactly once
- The total number of operations is proportional to the sum of the sizes of both arrays

Space Complexity: O(1)
- We use only a constant amount of extra space (three pointers)
- The merging is done in-place, using the existing space in nums1
"""

# Example test cases
if __name__ == "__main__":
    # Example 1
    nums1 = [1, 2, 3, 0, 0, 0]
    m = 3
    nums2 = [2, 5, 6]
    n = 3
    merge(nums1, m, nums2, n)
    print(nums1)  # Expected output: [1, 2, 2, 3, 5, 6]
    
    # Example 2
    nums1 = [1]
    m = 1
    nums2 = []
    n = 0
    merge(nums1, m, nums2, n)
    print(nums1)  # Expected output: [1]
    
    # Example 3
    nums1 = [0]
    m = 0
    nums2 = [1]
    n = 1
    merge(nums1, m, nums2, n)
    print(nums1)  # Expected output: [1]