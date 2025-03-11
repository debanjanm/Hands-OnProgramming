"""
LeetCode 169: Majority Element

1. Problem Statement:
Given an array nums of size n, return the majority element.

The majority element is the element that appears more than ⌊n/2⌋ times. 
You may assume that the majority element always exists in the array.

2. Code Implementation:
"""

def majority_element(nums):
    """
    Find the majority element in an array using Boyer-Moore Voting Algorithm.
    
    Args:
        nums (List[int]): Array of integers
        
    Returns:
        int: The majority element (appears more than n/2 times)
    """
    # Initialize candidate and count
    candidate = None
    count = 0
    
    # First pass: Find potential majority element
    for num in nums:
        # If count is 0, set current number as the candidate
        if count == 0:
            candidate = num
            count = 1
        # If current number matches candidate, increment count
        elif num == candidate:
            count += 1
        # If current number is different, decrement count
        else:
            count -= 1
    
    # The candidate at the end of the first pass is the majority element
    # (Since problem guarantees a majority element exists, we don't need a second pass to verify)
    return candidate

"""
3. Pattern Name:
Boyer-Moore Voting Algorithm

4. Explanation:
This problem asks us to find the majority element in an array, which is defined as an element 
that appears more than n/2 times (where n is the array length).

I've implemented the Boyer-Moore Voting Algorithm, which is an elegant and efficient solution:

1. The algorithm works by maintaining a candidate for the majority element and a count.

2. We iterate through the array once:
   - If count is 0, we set the current element as our candidate
   - If the current element matches our candidate, we increment the count
   - If the current element differs from our candidate, we decrement the count

3. The intuition behind this algorithm is that:
   - If an element is the majority, there will be more occurrences of it than all other elements combined
   - When count reaches 0, it means we've seen an equal number of our candidate and other elements
   - Since the majority element appears more than n/2 times, it will always be the final candidate

The beauty of this algorithm is that it only requires a single pass through the array and uses
constant extra space, regardless of the input size.

Alternative approaches:
1. HashMap approach: Count occurrences of each element and return the one with count > n/2
2. Sorting approach: Sort the array and return the middle element (it must be the majority)

5. Complexity Analysis:
Time Complexity: O(n)
- The algorithm only requires a single pass through the array, where n is the length of the array.
- Each element is processed in constant time.

Space Complexity: O(1)
- We only use two variables (candidate and count) regardless of the input size.
- This is more efficient than the hashmap approach, which would require O(n) space in the worst case.
"""

# Example test cases
if __name__ == "__main__":
    # Example 1
    nums = [3, 2, 3]
    print(majority_element(nums))  # Expected output: 3
    
    # Example 2
    nums = [2, 2, 1, 1, 1, 2, 2]
    print(majority_element(nums))  # Expected output: 2
    
    # Example 3
    nums = [1]
    print(majority_element(nums))  # Expected output: 1