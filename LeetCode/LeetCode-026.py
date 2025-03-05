"""
LeetCode Problem 26: Remove Duplicates from Sorted Array

1. Problem Statement:
Given an integer array 'nums' sorted in non-decreasing order, remove the duplicates in-place 
such that each unique element appears only once. The relative order of the elements should be 
kept the same. Then return the number of unique elements in 'nums'.

Consider the number of unique elements of 'nums' to be 'k', to get accepted, you need to do 
the following things:
- Change the array 'nums' such that the first 'k' elements of 'nums' contain the unique elements 
  in the order they were present in 'nums' initially.
- The first 'k' elements of 'nums' should be considered valid.
- Do not allocate extra space for another array. You must do this by modifying the input array 
  in-place with O(1) extra memory.

Example:
Input: nums = [1,1,2]
Output: 2, nums = [1,2,_]
Explanation: Your function should return k = 2, with the first two elements of nums being 1 and 2 
respectively. It does not matter what you leave beyond the returned k (hence they are underscores).
"""

from typing import List

class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        # Two-Pointer Approach
        # Handle edge case of empty array
        if not nums:
            return 0
        
        # Initialize the first pointer (unique element position)
        k = 1
        
        # Iterate through the array starting from the second element
        for i in range(1, len(nums)):
            # If current element is different from the previous unique element
            if nums[i] != nums[k-1]:
                # Place the current unique element in the next position
                nums[k] = nums[i]
                # Move the unique element pointer forward
                k += 1
        
        # Return the number of unique elements
        return k

# 3. Pattern Name:
# Two-Pointer Technique (In-place Array Modification)

"""
4. Explanation:
The solution uses a two-pointer approach to remove duplicates in-place:
1. We use two pointers:
   - 'i': Iterates through the entire array
   - 'k': Keeps track of the position where unique elements should be placed
2. Start with 'k' at 1, assuming the first element is always unique
3. Iterate through the array from the second element
4. Compare each element with the last unique element (nums[k-1])
5. If the current element is different:
   - Place it at the 'k' position
   - Increment 'k' to mark the next unique element position
6. This approach modifies the array in-place, keeping only unique elements
7. The first 'k' elements will contain the unique elements in their original order

5. Complexity Analysis:
- Time Complexity: O(n)
  - We iterate through the array only once
  - Each element is compared and potentially moved once
- Space Complexity: O(1)
  - We modify the array in-place
  - Only a constant amount of extra space is used (k pointer)

Key Characteristics:
- Works only on sorted arrays
- Modifies the input array directly
- Preserves the original order of elements
- Efficient single-pass solution

Alternative Approaches:
1. Using Set (not in-place):
   - Convert to set and back to list
   - Loses original order
   - Uses additional space
2. Naive approach with extra array
   - Creates a new array to store unique elements
   - Violates the in-place modification requirement
"""

# Example Usage
if __name__ == "__main__":
    solution = Solution()
    
    # Test Case 1
    nums1 = [1, 1, 2]
    k1 = solution.removeDuplicates(nums1)
    print(f"Test Case 1: k = {k1}, nums = {nums1[:k1]}")  # Expected: k = 2, nums = [1, 2]
    
    # Test Case 2
    nums2 = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]
    k2 = solution.removeDuplicates(nums2)
    print(f"Test Case 2: k = {k2}, nums = {nums2[:k2]}")  # Expected: k = 5, nums = [0, 1, 2, 3, 4]
    
    # Test Case 3 - Empty Array
    nums3 = []
    k3 = solution.removeDuplicates(nums3)
    print(f"Test Case 3: k = {k3}, nums = {nums3}")  # Expected: k = 0, nums = []