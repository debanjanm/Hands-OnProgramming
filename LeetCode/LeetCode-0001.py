"""
LeetCode Problem 1: Two Sum

1. Problem Statement:
Given an array of integers 'nums' and an integer 'target', return indices of the two numbers 
such that they add up to the target. You may assume that each input would have exactly one solution, 
and you may not use the same element twice. You can return the answer in any order.

Example:
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1]
"""

from typing import List

class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        # Hash Map Solution
        # Create a dictionary to store complement values
        num_map = {}
        
        # Iterate through the array
        for i, num in enumerate(nums):
            # Calculate the complement needed to reach the target
            complement = target - num
            
            # Check if the complement exists in the map
            if complement in num_map:
                # Return the indices of the two numbers
                return [num_map[complement], i]
            
            # Store the current number and its index
            num_map[num] = i
        
        # If no solution is found (though problem guarantees one exists)
        return []

# 3. Pattern Name:
# Hash Map / Dictionary-based Solution (One-pass Hash Table)

"""
4. Explanation:
The solution uses a hash map (dictionary in Python) to achieve O(n) time complexity.
Key steps:
1. Create an empty dictionary to store numbers and their indices
2. Iterate through the array once
3. For each number, calculate its complement (target - current number)
4. Check if the complement exists in the dictionary
   - If it does, we've found our pair and return their indices
   - If not, add the current number and its index to the dictionary
5. This approach allows us to find the solution in a single pass

5. Complexity Analysis:
- Time Complexity: O(n)
  - We iterate through the array only once
  - Dictionary lookup is O(1) on average
- Space Complexity: O(n)
  - In the worst case, we might need to store almost all numbers in the dictionary
  - Each number is stored once before finding its complement

Alternative Approaches:
1. Brute Force: 
   - Use nested loops to check every pair
   - Time Complexity: O(n²)
   - Space Complexity: O(1)

2. Two-pass Hash Table:
   - First pass: Build the hash table
   - Second pass: Find the complement
   - Time Complexity: O(n)
   - Space Complexity: O(n)

This One-pass Hash Table approach is the most efficient for this problem.
"""

# Example Usage
if __name__ == "__main__":
    solution = Solution()
    
    # Test Case 1
    nums1 = [2, 7, 11, 15]
    target1 = 9
    print(f"Test Case 1: {solution.twoSum(nums1, target1)}")  # Expected: [0, 1]
    
    # Test Case 2
    nums2 = [3, 2, 4]
    target2 = 6
    print(f"Test Case 2: {solution.twoSum(nums2, target2)}")  # Expected: [1, 2]
    
    # Test Case 3
    nums3 = [3, 3]
    target3 = 6
    print(f"Test Case 3: {solution.twoSum(nums3, target3)}")  # Expected: [0, 1]