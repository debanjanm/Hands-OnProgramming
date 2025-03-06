"""
LeetCode Problem 2006: Count Number of Pairs With Absolute Difference K

1. Problem Statement:
Given an integer array nums and an integer k, return the number of pairs (i, j) 
where i < j such that |nums[i] - nums[j]| == k.

The absolute difference between two numbers is the absolute value of their difference.

Example 1:
Input: nums = [1,2,2,1], k = 1
Output: 4
Explanation: The pairs with an absolute difference of 1 are:
- [1,2] at indices (0,1)
- [2,1] at indices (1,3)
- [1,2] at indices (0,2)
- [2,1] at indices (2,3)

Example 2:
Input: nums = [1,3], k = 3
Output: 1
Explanation: The only pair with an absolute difference of 3 is [1,3] at indices (0,1).

Example 3:
Input: nums = [3,2,1,5,4], k = 2
Output: 3
Explanation: The pairs with an absolute difference of 2 are:
- [3,1] at indices (0,2)
- [3,5] at indices (0,3)
- [2,4] at indices (1,4)
"""

from typing import List
from collections import Counter

class Solution:
    def countKDifference(self, nums: List[int], k: int) -> int:
        # Hash Map approach
        count = 0
        num_counter = Counter()
        
        # Process each number in the array
        for num in nums:
            # For each number, check how many numbers already exist in our counter
            # that would make a valid pair with absolute difference k
            count += num_counter[num - k]  # nums[i] = num - k, nums[j] = num
            count += num_counter[num + k]  # nums[i] = num + k, nums[j] = num
            
            # Add current number to counter after checking
            num_counter[num] += 1
        
        return count
    
    # Alternative method using pre-populated counter
    def countKDifference_alt(self, nums: List[int], k: int) -> int:
        count = 0
        counter = Counter(nums)
        
        # Special case for k = 0
        if k == 0:
            # For k=0, we need to calculate combinations: n*(n-1)/2 for each number with count > 1
            for num, freq in counter.items():
                if freq > 1:
                    count += (freq * (freq - 1)) // 2
            return count
        
        # For k > 0, we check each unique number and its potential pair
        for num, freq in counter.items():
            # Only check num + k to avoid double counting
            if num + k in counter:
                count += freq * counter[num + k]
        
        return count
    
    # Brute force method for comparison
    def countKDifference_brute_force(self, nums: List[int], k: int) -> int:
        count = 0
        n = len(nums)
        
        for i in range(n):
            for j in range(i + 1, n):
                if abs(nums[i] - nums[j]) == k:
                    count += 1
        
        return count

# 3. Pattern Name:
# Hash Map / Frequency Counter with Complement Search

"""
4. Explanation:
The solution uses a Hash Map (Counter in Python) to efficiently count pairs:

Main Solution (countKDifference):
1. We process numbers one by one and build a frequency counter as we go
2. For each number 'num', we check for two potential complements in our counter:
   - 'num - k': Numbers that would be k less than the current number
   - 'num + k': Numbers that would be k more than the current number
3. We add these counts to our running total BEFORE adding the current number to the counter
4. This approach ensures we only count pairs where i < j (as required by the problem)

Alternative Solution (countKDifference_alt):
1. First create a complete frequency counter for all numbers
2. Handle k=0 as a special case:
   - For each number with frequency > 1, calculate combinations: freq*(freq-1)/2
3. For k>0:
   - For each unique number, check if its complement (num + k) also exists
   - If both exist, we can form counter[num] * counter[num + k] pairs

Key Insight:
- If |nums[i] - nums[j]| = k, then either nums[j] = nums[i] + k or nums[j] = nums[i] - k
- For k=0, we need to be careful about counting pairs within the same number

5. Complexity Analysis:
- Time Complexity: O(n)
  - We iterate through the array once
  - Each lookup and update operation in the counter is O(1)
  
- Space Complexity: O(n)
  - In the worst case, all numbers in the array are unique
  - The counter would store at most n entries

Comparison with Brute Force:
- Brute Force solution requires checking all possible pairs
  - Time Complexity: O(n²)
  - Space Complexity: O(1)
"""

# Example Usage
if __name__ == "__main__":
    solution = Solution()
    
    # Test Case 1
    nums1 = [1, 2, 2, 1]
    k1 = 1
    print(f"Test Case 1: {solution.countKDifference(nums1, k1)}")  # Expected: 4
    print(f"Alt Solution: {solution.countKDifference_alt(nums1, k1)}")
    print(f"Brute Force: {solution.countKDifference_brute_force(nums1, k1)}")
    
    # Test Case 2
    nums2 = [1, 3]
    k2 = 3
    print(f"Test Case 2: {solution.countKDifference(nums2, k2)}")  # Expected: 1
    print(f"Alt Solution: {solution.countKDifference_alt(nums2, k2)}")
    print(f"Brute Force: {solution.countKDifference_brute_force(nums2, k2)}")
    
    # Test Case 3
    nums3 = [3, 2, 1, 5, 4]
    k3 = 2
    print(f"Test Case 3: {solution.countKDifference(nums3, k3)}")  # Expected: 3
    print(f"Alt Solution: {solution.countKDifference_alt(nums3, k3)}")
    print(f"Brute Force: {solution.countKDifference_brute_force(nums3, k3)}")
    
    # Test Case 4 - Special case for k=0
    nums4 = [1, 1, 1, 1]
    k4 = 0
    print(f"Test Case 4: {solution.countKDifference(nums4, k4)}")  # Expected: 6
    print(f"Alt Solution: {solution.countKDifference_alt(nums4, k4)}")
    print(f"Brute Force: {solution.countKDifference_brute_force(nums4, k4)}")