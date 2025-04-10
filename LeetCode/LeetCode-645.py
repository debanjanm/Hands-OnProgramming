"""
LeetCode 645. Set Mismatch

1. Problem Statement:
You have a set of integers s, which originally contains all the numbers from 1 to n. 
Unfortunately, due to some error, one of the numbers in s got duplicated to another number in the set, 
which results in repetition of one number and loss of another number.

You are given an array nums representing the data status of this set after the error.
Find the number that occurs twice and the number that is missing and return them in the form of an array.

2. Code Implementation:
"""

def findErrorNums(nums):
    """
    Finds the duplicate and missing numbers in the input array.
    
    Args:
        nums: List[int] - An array of integers from 1 to n with one duplicate and one missing
        
    Returns:
        List[int] - [duplicate_number, missing_number]
    """
    n = len(nums)
    num_set = set()
    duplicate = -1
    
    # Find the duplicate number
    for num in nums:
        if num in num_set:
            duplicate = num
        else:
            num_set.add(num)
    
    # Find the missing number
    for i in range(1, n + 1):
        if i not in num_set:
            return [duplicate, i]
    
    # This should not happen given the problem constraints
    return [duplicate, -1]

"""
3. Pattern Name:
Hash Set / Array Manipulation Pattern

4. Explanation:
This problem asks us to find two special numbers in an array:
1. A duplicate number (occurs twice)
2. A missing number (should be in range 1...n but isn't present)

The approach used:
1. Create a set to track the numbers we've seen
2. Iterate through the input array:
   - If we encounter a number already in our set, we've found the duplicate
   - Otherwise, add the number to our set
3. Iterate through the range 1 to n:
   - If any number in this range is not in our set, it's the missing number
4. Return the duplicate and missing numbers

The key insight is using a set for O(1) lookups to efficiently identify both the 
duplicate and missing numbers. This approach handles the constraints of the problem 
where we know there's exactly one duplicate and one missing number.

5. Complexity Analysis:
- Time Complexity: O(n)
  - We iterate through the array once to find the duplicate: O(n)
  - We then potentially check each number from 1 to n: O(n)
  - Set operations (add, lookup) are O(1) on average
  
- Space Complexity: O(n)
  - We use a set that can store up to n-1 unique elements
  - The output array is constant space O(1) as it always contains exactly 2 elements

Alternative Approaches:
1. Math approach: Calculate the expected sum (n(n+1)/2) and the sum of set of unique elements.
   The difference between expected sum and actual sum helps find the missing number.
   
2. Bit manipulation: XOR all numbers and all indices (1 to n) together.
   This cancels out all numbers except the duplicate and missing ones.
   
3. In-place marking: Use the array indices to mark visited numbers, but requires modifying the array.
"""

# Example usage
if __name__ == "__main__":
    nums1 = [1, 2, 2, 4]
    print(findErrorNums(nums1))  # Expected output: [2, 3]
    
    nums2 = [1, 1]
    print(findErrorNums(nums2))  # Expected output: [1, 2]