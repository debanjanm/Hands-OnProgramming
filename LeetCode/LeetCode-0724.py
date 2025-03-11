"""
LeetCode 724: Find Pivot Index

1. Problem Statement:
Given an array of integers nums, calculate the pivot index of this array.

The pivot index is the index where the sum of all the numbers strictly to the left of the index is equal to the sum of all the numbers strictly to the right of the index.

If the index is on the left edge of the array, then the left sum is 0 because there are no elements to the left. This also applies to the right edge of the array.

Return the leftmost pivot index. If no such index exists, return -1.

2. Code Implementation:
"""

def pivot_index(nums):
    """
    Find the pivot index in an array where sum of elements to the left equals sum of elements to the right.
    
    Args:
        nums (List[int]): Array of integers
        
    Returns:
        int: The pivot index, or -1 if none exists
    """
    # Calculate the total sum of the array
    total_sum = sum(nums)
    
    # Initialize left_sum to track the running sum from left
    left_sum = 0
    
    # Iterate through the array
    for i, num in enumerate(nums):
        # Right sum is the total sum minus left sum and current element
        right_sum = total_sum - left_sum - num
        
        # Check if this is a pivot index
        if left_sum == right_sum:
            return i
        
        # Update left_sum for the next iteration
        left_sum += num
    
    # If we get here, no pivot index was found
    return -1

"""
3. Pattern Name:
Prefix Sum / Running Sum

4. Explanation:
This problem asks us to find an index in the array where the sum of elements to the left equals the sum of elements to the right.

The approach uses the concept of prefix sums to efficiently solve this problem:

1. First, we calculate the total sum of all elements in the array.

2. Then, we iterate through the array while maintaining a running sum of elements seen so far (left_sum).

3. For each index i, we can calculate the right_sum without actually summing all the elements to the right:
   right_sum = total_sum - left_sum - nums[i]
   This formula works because:
   - total_sum includes all elements
   - left_sum is the sum of elements before the current index
   - nums[i] is the current element
   - Therefore, right_sum must be what remains

4. If left_sum equals right_sum at any index, we've found a pivot index and return it.

5. If we finish iterating without finding such an index, we return -1.

This approach is efficient because:
- We only need to traverse the array once
- We avoid recalculating sums repeatedly
- We leverage mathematical properties to minimize operations

The solution correctly handles edge cases:
- Empty arrays (total_sum will be 0, no valid pivot)
- Pivot at index 0 (left_sum is 0)
- Pivot at the last index (right_sum is 0)
- Negative numbers in the array

5. Complexity Analysis:
Time Complexity: O(n)
- Calculating the total sum requires one pass through the array: O(n)
- The main algorithm requires one more pass through the array: O(n)
- Overall time complexity is O(n), where n is the length of the input array

Space Complexity: O(1)
- We only use a constant amount of extra space (total_sum and left_sum variables)
- The solution doesn't create any data structures that scale with input size
"""

# Example test cases
if __name__ == "__main__":
    # Example 1
    nums = [1, 7, 3, 6, 5, 6]
    print(pivot_index(nums))  # Expected output: 3
    
    # Example 2
    nums = [1, 2, 3]
    print(pivot_index(nums))  # Expected output: -1
    
    # Example 3
    nums = [2, 1, -1]
    print(pivot_index(nums))  # Expected output: 0
    
    # Example 4
    nums = [-1, -1, -1, 1, 1, 1]
    print(pivot_index(nums))  # Expected output: -1