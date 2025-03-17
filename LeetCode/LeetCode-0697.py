"""
LeetCode 697: Degree of an Array

1. Problem Statement:
Given a non-empty array of non-negative integers nums, the degree of this array is defined as the maximum frequency of any one of its elements.

Your task is to find the smallest possible length of a (contiguous) subarray of nums, that has the same degree as nums.

2. Code Implementation:
"""

def find_shortest_subarray(nums):
    """
    Find the length of the shortest subarray with the same degree as the original array.
    
    Args:
        nums (List[int]): A non-empty array of non-negative integers
        
    Returns:
        int: The length of the shortest subarray with the same degree
    """
    # Dictionary to store first occurrence of each number
    first_occurrence = {}
    
    # Dictionary to store last occurrence of each number
    last_occurrence = {}
    
    # Dictionary to store frequency of each number
    frequency = {}
    
    # Process all elements in the array
    for i, num in enumerate(nums):
        # Update first occurrence (only if this is the first time we see this number)
        if num not in first_occurrence:
            first_occurrence[num] = i
        
        # Update last occurrence
        last_occurrence[num] = i
        
        # Update frequency
        frequency[num] = frequency.get(num, 0) + 1
    
    # Find the degree of the array
    max_freq = max(frequency.values())
    
    # Find the smallest subarray length with the same degree
    min_length = len(nums)
    for num in frequency:
        if frequency[num] == max_freq:
            # Length of subarray with this number = last occurrence - first occurrence + 1
            subarray_length = last_occurrence[num] - first_occurrence[num] + 1
            min_length = min(min_length, subarray_length)
    
    return min_length

"""
3. Pattern Name:
Hash Map / Array Analysis

4. Explanation:
This problem requires us to find the shortest contiguous subarray that has the same degree as the original array.
The "degree" of an array is defined as the maximum frequency of any element within it.

The approach:
1. We need to track three pieces of information for each element:
   - Its first occurrence (index)
   - Its last occurrence (index)
   - Its frequency in the array

2. We use three dictionaries to store this information:
   - first_occurrence: Maps each number to the index of its first occurrence
   - last_occurrence: Maps each number to the index of its last occurrence
   - frequency: Maps each number to its frequency in the array

3. After processing the entire array, we:
   - Find the maximum frequency (degree of the array)
   - For each element with this maximum frequency, calculate the length of the subarray
     that contains all occurrences of this element (last_occurrence - first_occurrence + 1)
   - Return the minimum of these lengths

This approach works because:
- Any subarray with the same degree must contain all instances of at least one element with
  the maximum frequency
- The shortest such subarray must start at the first occurrence and end at the last occurrence
  of one of these elements
- We check all elements with the maximum frequency to find the one that gives the shortest subarray

5. Complexity Analysis:
Time Complexity: O(n)
- We iterate through the array once to build our dictionaries: O(n)
- Finding the maximum frequency is O(n) in the worst case
- Iterating through the elements with the maximum frequency is O(n) in the worst case
- Overall time complexity is O(n), where n is the length of the input array

Space Complexity: O(k)
- We use three dictionaries, each with at most k entries, where k is the number of unique elements in the array
- In the worst case, all elements are unique, so k = n
- Therefore, the space complexity is O(k), which could be O(n) in the worst case
"""

# Example test cases
if __name__ == "__main__":
    # Example 1
    nums = [1, 2, 2, 3, 1]
    print(find_shortest_subarray(nums))  # Expected output: 2
    
    # Example 2
    nums = [1, 2, 2, 3, 1, 4, 2]
    print(find_shortest_subarray(nums))  # Expected output: 6
    
    # Example 3
    nums = [1, 1, 2, 2, 2, 1]
    print(find_shortest_subarray(nums))  # Expected output: 3
    
    # Example 4
    nums = [1, 3, 2, 2, 3, 1]
    print(find_shortest_subarray(nums))  # Expected output: 2