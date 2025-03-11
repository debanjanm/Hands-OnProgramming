"""
LeetCode 2154: Keep Multiplying Found Values by Two

1. Problem Statement:
You are given an array of integers nums. You are also given an integer original which is the first number that needs to be searched for in nums.

You then do the following steps:
1. If original is found in nums, multiply original by 2 (i.e., set original = 2 * original).
2. Otherwise, stop the process.
3. Repeat this process with the new value of original.

Return the final value of original.

2. Code Implementation:
"""

def find_final_value(nums, original):
    """
    Returns the final value of original after repeatedly multiplying by 2 when found in nums.
    
    Args:
        nums (List[int]): Array of integers
        original (int): The initial value to search for
        
    Returns:
        int: The final value of original after the process
    """
    # Convert nums to a set for O(1) lookups
    num_set = set(nums)
    
    # Keep multiplying original by 2 as long as it's found in the set
    while original in num_set:
        original *= 2
    
    return original

"""
3. Pattern Name:
Set Membership / Array Search

4. Explanation:
This problem asks us to find a value in an array, and if found, double it and search again
until the value is no longer present in the array.

The approach:
1. First, I convert the input array to a set for efficient lookups. This gives us O(1) time 
   complexity for checking if a value exists, rather than O(n) if we were to scan the array 
   each time.
   
2. Then, we enter a while loop that continues as long as the current value of 'original' 
   is found in our set.
   
3. Inside the loop, whenever 'original' is found, we multiply it by 2 as per the problem's 
   requirement.
   
4. The loop terminates when 'original' is no longer found in the set, and we return 
   the final value.

This solution is efficient because it:
- Uses a set for O(1) lookups instead of repeatedly scanning the array
- Only performs the minimum number of operations needed
- Has a clear termination condition

5. Complexity Analysis:
Time Complexity: O(n + log m)
- Converting the array to a set takes O(n) time, where n is the length of the input array.
- The while loop iterates at most O(log m) times, where m is the maximum possible value 
  in the array. This is because each iteration doubles the value of 'original', so the 
  number of iterations is logarithmic in the maximum value.
- Note that in practice, the number of iterations is limited by the largest value in the 
  array, so it's often much smaller than log(m).

Space Complexity: O(n)
- We use a set to store all elements from the input array, which takes O(n) space.
- No additional data structures are used that scale with input size.
"""

# Example test cases
if __name__ == "__main__":
    # Example 1
    nums = [5, 3, 6, 1, 12]
    original = 3
    print(find_final_value(nums, original))  # Expected output: 24
    
    # Example 2
    nums = [2, 7, 9]
    original = 4
    print(find_final_value(nums, original))  # Expected output: 4
    
    # Example 3
    nums = [8, 19, 4, 2, 15, 3]
    original = 2
    print(find_final_value(nums, original))  # Expected output: 16
