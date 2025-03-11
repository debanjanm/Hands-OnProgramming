"""
66. Plus One

1. Problem Statement:
You are given a large integer represented as an integer array digits, where each digits[i] is the ith digit of the integer.
The digits are ordered from most significant to least significant in left-to-right order.
The large integer does not contain any leading 0's.
Increment the large integer by one and return the resulting array of digits.

2. Code Implementation:
"""

class Solution:
    def plusOne(self, digits: list[int]) -> list[int]:
        n = len(digits)
        
        # Start from the last digit
        for i in range(n - 1, -1, -1):
            # If the current digit is less than 9, simply increment it and return
            if digits[i] < 9:
                digits[i] += 1
                return digits
            # Otherwise, set the current digit to 0 and continue to the next digit
            digits[i] = 0
        
        # If we're here, it means all digits were 9's
        # Insert 1 at the beginning of the array
        return [1] + digits

"""
3. Pattern Name:
Array Traversal and Carry Handling

4. Explanation:
This problem involves adding 1 to a number represented as an array of digits. The key insight is handling the "carry" when a digit becomes 10.

The solution works as follows:
- Traverse the array from right to left (least significant to most significant digit)
- If the current digit is less than 9, add 1 to it and return the array immediately
- If the current digit is 9, set it to 0 and continue to the next digit (carrying the 1)
- If all digits are 9, then we need to add a new digit (1) at the beginning of the array

Example:
- Input: [1,2,3]
  - Last digit 3 < 9, so add 1: [1,2,4]
  - Return [1,2,4]
- Input: [9,9,9]
  - Last digit is 9, set to 0: [9,9,0]
  - Middle digit is 9, set to 0: [9,0,0]
  - First digit is 9, set to 0: [0,0,0]
  - All digits were 9, so add 1 at beginning: [1,0,0,0]

5. Complexity Analysis:
- Time Complexity: O(n) where n is the number of digits
  - In the worst case (all 9's), we need to traverse all digits once
  - In the best case (last digit < 9), we only check one digit, making it O(1)
- Space Complexity: O(1) if we don't count the output array
  - In the worst case (all 9's), we create a new array with one extra digit, which would be O(n)
  - Otherwise, we just modify the input array in-place
"""

# Test cases
if __name__ == "__main__":
    solution = Solution()
    
    # Test case 1: Regular case
    print(solution.plusOne([1, 2, 3]))  # Output: [1, 2, 4]
    
    # Test case 2: Carry case
    print(solution.plusOne([4, 3, 2, 1]))  # Output: [4, 3, 2, 2]
    
    # Test case 3: All 9's case
    print(solution.plusOne([9, 9]))  # Output: [1, 0, 0]