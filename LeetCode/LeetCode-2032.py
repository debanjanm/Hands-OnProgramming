"""
LeetCode 2032: Two Out of Three

1. Problem Statement:
Given three integer arrays nums1, nums2, and nums3, return a distinct array containing all the values that are present in at least two out of the three arrays. You may return the values in any order.

2. Code Implementation:
"""

def two_out_of_three(nums1, nums2, nums3):
    """
    Return all distinct values that appear in at least two of the three input arrays.
    
    Args:
        nums1 (List[int]): First array of integers
        nums2 (List[int]): Second array of integers
        nums3 (List[int]): Third array of integers
        
    Returns:
        List[int]: Distinct integers that appear in at least two arrays
    """
    # Convert to sets to eliminate duplicates within each array
    set1 = set(nums1)
    set2 = set(nums2)
    set3 = set(nums3)
    
    # Initialize result list
    result = []
    
    # Check each unique number from all arrays
    all_unique_nums = set1.union(set2).union(set3)
    
    for num in all_unique_nums:
        # Count how many arrays contain this number
        count = 0
        if num in set1:
            count += 1
        if num in set2:
            count += 1
        if num in set3:
            count += 1
        
        # If number appears in at least 2 arrays, add to result
        if count >= 2:
            result.append(num)
    
    return result

"""
3. Pattern Name:
Set Operations / Hash Set

4. Explanation:
This problem requires us to find elements that appear in at least two of the three given arrays.
The approach uses set operations to efficiently solve the problem:

1. First, we convert each input array to a set to eliminate duplicates within each array.
   This is important because we only care if a number appears in an array, not how many times.

2. We create a union of all three sets to get all unique numbers across all arrays.

3. For each unique number, we count how many of the original arrays contain it by 
   checking membership in each set.

4. If a number appears in two or more sets (meaning it appears in at least two arrays),
   we add it to our result list.

This approach is clean and efficient as set membership testing is O(1) on average.

Alternative approach:
We could also solve this problem by using a Counter or frequency dictionary:
- Create a set for each array to remove duplicates
- For each unique number across all arrays, count how many sets contain it
- Add numbers with count >= 2 to the result

5. Complexity Analysis:
Time Complexity: O(n1 + n2 + n3)
- Converting arrays to sets takes O(n1 + n2 + n3) time, where n1, n2, and n3 are the lengths
  of the input arrays.
- The union operation takes O(n1 + n2 + n3) in the worst case.
- Iterating through the union and checking membership in each set takes O(n1 + n2 + n3)
  with O(1) membership checks.

Space Complexity: O(n1 + n2 + n3)
- We store the distinct elements from each array in three sets.
- The union set contains at most n1 + n2 + n3 elements.
- The result list contains at most n1 + n2 + n3 elements.
"""

# Example test cases
if __name__ == "__main__":
    # Example 1
    nums1 = [1, 1, 3, 2]
    nums2 = [2, 3]
    nums3 = [3]
    print(two_out_of_three(nums1, nums2, nums3))  # Expected output: [3, 2]
    
    # Example 2
    nums1 = [3, 1]
    nums2 = [2, 3]
    nums3 = [1, 2]
    print(two_out_of_three(nums1, nums2, nums3))  # Expected output: [2, 3, 1]
    
    # Example 3
    nums1 = [1, 2, 2]
    nums2 = [4, 3, 3]
    nums3 = [5]
    print(two_out_of_three(nums1, nums2, nums3))  # Expected output: []