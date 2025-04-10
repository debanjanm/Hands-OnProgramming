"""
LeetCode 2570. Merge Two 2D Arrays by Summing Values

1. Problem Statement:
You are given two 2D integer arrays nums1 and nums2.
- nums1[i] = [idi, vali] indicate that the number with the id idi has a value equal to vali.
- nums2[i] = [idi, vali] indicate that the number with the id idi has a value equal to vali.

Each array contains unique ids and is sorted by ids in ascending order.

Merge the two arrays into one array that is sorted by ids in ascending order. If there are two entries with the same id, the value should be the sum of the two values.

2. Code Implementation:
"""

def mergeArrays(nums1, nums2):
    """
    Merges two 2D arrays by summing values with the same id.
    
    Args:
        nums1: List[List[int]] - First 2D array with [id, value] pairs
        nums2: List[List[int]] - Second 2D array with [id, value] pairs
        
    Returns:
        List[List[int]] - Merged array with summed values for same ids
    """
    # Create a dictionary to store id -> value mappings
    merged_dict = {}
    
    # Process the first array
    for id_val, value in nums1:
        merged_dict[id_val] = value
    
    # Process the second array, adding values for existing ids
    for id_val, value in nums2:
        if id_val in merged_dict:
            merged_dict[id_val] += value
        else:
            merged_dict[id_val] = value
    
    # Convert the dictionary back to the required list format
    # and sort by id (which is the key in our dictionary)
    result = [[id_val, value] for id_val, value in merged_dict.items()]
    result.sort()  # Sort by id
    
    return result

"""
3. Pattern Name:
Hash Map / Dictionary Merging Pattern

4. Explanation:
This problem essentially asks us to merge two arrays where each element is an [id, value] pair.
The merging process requires summing values for matching ids.

The approach used is:
1. Create a dictionary to track id -> value mappings
2. Iterate through the first array, storing each id and its value in the dictionary
3. Iterate through the second array:
   - If the id already exists in our dictionary, add the new value to the existing value
   - If the id doesn't exist, add a new entry in the dictionary
4. Convert the dictionary back to the required 2D array format
5. Sort the result by id

This approach is efficient because dictionary lookups are O(1) on average,
making the merging process straightforward and fast.

5. Complexity Analysis:
- Time Complexity: O((n + m) log(n + m))
  - O(n) for processing the first array (n is the length of nums1)
  - O(m) for processing the second array (m is the length of nums2)
  - O((n + m) log(n + m)) for sorting the final result
  - The dictionary operations are O(1) on average
  
- Space Complexity: O(n + m)
  - We use a dictionary that might contain up to n + m unique ids
  - The final result array will also have size O(n + m)

Note: If the arrays are already sorted by id (as specified in the problem), 
we could use a two-pointer approach without a dictionary to achieve O(n + m) time complexity.
However, the dictionary approach is more intuitive and still offers good performance.
"""

# Example usage
if __name__ == "__main__":
    nums1 = [[1, 2], [2, 3], [4, 5]]
    nums2 = [[1, 4], [3, 2], [4, 1]]
    print(mergeArrays(nums1, nums2))  # Expected output: [[1, 6], [2, 3], [3, 2], [4, 6]]