"""
LeetCode 896: Monotonic Array
============================

1. Problem Statement
-------------------
An array is monotonic if it is either monotone increasing or monotone decreasing.

An array nums is monotone increasing if for all i <= j, nums[i] <= nums[j].
An array nums is monotone decreasing if for all i <= j, nums[i] >= nums[j].

Given an integer array nums, return true if the given array is monotonic, or false otherwise.

2. Code Implementation
--------------------
"""

def isMonotonic(nums):
    """
    :type nums: List[int]
    :rtype: bool
    """
    # Edge cases
    if len(nums) <= 2:
        return True
    
    # Determine if the array should be increasing or decreasing
    increasing = decreasing = True
    
    # Check monotonicity by iterating through the array once
    for i in range(1, len(nums)):
        if nums[i] < nums[i-1]:
            increasing = False
        if nums[i] > nums[i-1]:
            decreasing = False
        
        # Early termination - if array is neither increasing nor decreasing
        if not increasing and not decreasing:
            return False
    
    # If we've made it through the loop, the array is either increasing or decreasing
    return True

"""
3. Pattern Name
--------------
This problem is an example of the "Array Traversal" pattern with a "Flag-based State Tracking" technique.

4. Explanation
------------
The solution works by:
1. Handling edge cases: arrays with 0, 1, or 2 elements are always monotonic by definition.
2. Using two boolean flags to track whether the array could be monotonically increasing or decreasing.
3. Traversing the array once, comparing adjacent elements:
   - If we find a pair where current > previous, the array cannot be decreasing
   - If we find a pair where current < previous, the array cannot be increasing
4. If at any point both flags become False, we can immediately return False
5. Otherwise, we return True after checking all elements

Alternative approaches:
- We could do two separate passes: one to check if it's increasing, another to check if it's decreasing
- We could determine the direction from the first and last elements, then verify that direction

5. Complexity Analysis
--------------------
Time Complexity: O(n) where n is the length of the array
- We traverse the array exactly once

Space Complexity: O(1)
- We only use two boolean variables regardless of input size
- No additional data structures are used

"""

# Test cases
test_cases = [
    [1, 2, 2, 3],       # True (increasing)
    [6, 5, 4, 4],       # True (decreasing)
    [1, 3, 2],          # False
    [1, 2, 4, 5],       # True (increasing)
    [1, 1, 1],          # True (both)
    [],                 # True (edge case)
    [42]                # True (edge case)
]

for i, test in enumerate(test_cases):
    result = isMonotonic(test)
    print(f"Test {i+1}: {test} -> {result}")