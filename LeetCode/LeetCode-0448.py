"""
LeetCode 448: Find All Numbers Disappeared in an Array
====================================================

1. Problem Statement
-------------------
Given an array nums of n integers where nums[i] is in the range [1, n], return an array of all the integers in the range [1, n] that do not appear in nums.

You must write an algorithm that runs in O(n) time and uses only constant extra space.

2. Code Implementation
--------------------
"""

def findDisappearedNumbers(nums):
    """
    :type nums: List[int]
    :rtype: List[int]
    """
    # Mark the numbers that are present
    for num in nums:
        # Get the absolute value in case we've already marked this index
        index = abs(num) - 1
        # Mark by making the number at that index negative
        if nums[index] > 0:
            nums[index] = -nums[index]
    
    # Find indices that still have positive values
    # (these indices + 1 are the missing numbers)
    result = []
    for i in range(len(nums)):
        if nums[i] > 0:
            result.append(i + 1)
    
    return result

"""
3. Pattern Name
--------------
This problem demonstrates the "Array Indexing as a Hash Map" pattern, also known as "In-place Array Marking".

4. Explanation
------------
The key insight to this problem is that we need to find all numbers in range [1, n] that don't appear in the array,
without using extra space. The clever approach is to use the array itself as a hash map.

How the solution works:
1. Since all numbers are in range [1, n], we can use the value as an index into the array (with adjustment since arrays are 0-indexed).
2. For each number in the array, we mark the presence of that number by making the number at the corresponding index negative.
3. After one pass, any index that still has a positive value corresponds to a number that didn't appear in the array.

For example, with array [4,3,2,7,8,2,3,1]:
- We see 4, marking the 4th position (index 3) by making it negative: [4,3,2,-7,8,2,3,1]
- We process 3, marking the 3rd position (index 2): [4,3,-2,-7,8,2,3,1]
- And so on...
- After marking all numbers, indices with positive values (0 and 4) correspond to missing numbers (1 and 5)

This approach:
- Preserves the original values (we can get them back by taking absolute values)
- Uses the array values as markers for presence/absence
- Works in O(n) time and O(1) extra space as required

5. Complexity Analysis
--------------------
Time Complexity: O(n) 
- We traverse the array twice, each taking O(n) time
- First to mark the presence of numbers
- Second to find the indices that still have positive values

Space Complexity: O(1) 
- We use the input array itself to track information
- The result array doesn't count toward space complexity in this type of problem
- Only a constant amount of extra variables are used

"""

# Test cases
test_cases = [
    [4, 3, 2, 7, 8, 2, 3, 1],  # Expected: [5, 6]
    [1, 1],                    # Expected: [2]
    [1, 2, 3, 4, 5],           # Expected: []
    [2, 2],                    # Expected: [1]
]

for i, test in enumerate(test_cases):
    # Create a copy to avoid modifying the original test case
    result = findDisappearedNumbers(test.copy())
    print(f"Test {i+1}: Input array = {test}, Missing numbers = {result}")