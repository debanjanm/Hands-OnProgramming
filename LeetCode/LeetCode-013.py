"""
LeetCode Problem 13: Roman to Integer

1. Problem Statement:
Roman numerals are represented by seven different symbols:
I = 1
V = 5
X = 10
L = 50
C = 100
D = 500
M = 1000

Roman numerals are usually written from largest to smallest from left to right. 
However, the numeral for four is not IIII but IV (5 - 1), and similarly, 
the numeral for nine is IX (10 - 1).

Given a roman numeral string, convert it to an integer.

Example 1:
Input: s = "III"
Output: 3
Explanation: III = 3

Example 2:
Input: s = "LVIII"
Output: 58
Explanation: L = 50, V = 5, III = 3

Example 3:
Input: s = "MCMXCIV"
Output: 1994
Explanation: M = 1000, CM = 900, XC = 90, IV = 4
"""

class Solution:
    def romanToInt(self, s: str) -> int:
        # Mapping of Roman numeral symbols to their integer values
        roman_values = {
            'I': 1,
            'V': 5,
            'X': 10,
            'L': 50,
            'C': 100,
            'D': 500,
            'M': 1000
        }
        
        # Initialize total sum
        total = 0
        
        # Iterate through the string
        for i in range(len(s)):
            # If current symbol's value is less than the next symbol's value,
            # it means we have a subtraction case (like IV, IX, XC)
            if i < len(s) - 1 and roman_values[s[i]] < roman_values[s[i+1]]:
                total -= roman_values[s[i]]
            else:
                total += roman_values[s[i]]
        
        return total

# 3. Pattern Name:
# Iterative Symbol Mapping with Lookahead Strategy

"""
4. Explanation:
The solution uses a straightforward iterative approach to convert Roman numerals:

Key Steps:
1. Create a dictionary mapping Roman symbols to their integer values
2. Initialize a total sum variable
3. Iterate through each character in the Roman numeral string
4. Use a lookahead strategy to handle subtraction cases:
   - Normally, add the value of the current symbol
   - If the current symbol's value is less than the next symbol's value,
     subtract the current symbol's value instead of adding
5. This handles special cases like IV (4), IX (9), XL (40), XC (90), etc.

Subtraction Rule Examples:
- IV = 5 - 1 = 4
- IX = 10 - 1 = 9
- XL = 50 - 10 = 40
- XC = 100 - 10 = 90
- CM = 1000 - 100 = 900

5. Complexity Analysis:
- Time Complexity: O(n)
  - We iterate through the string only once
  - Each character is processed in constant time
- Space Complexity: O(1)
  - We use a fixed-size dictionary (7 entries)
  - Only a constant amount of extra space is used

Constraints and Limitations:
- Assumes valid Roman numeral input
- Supports standard Roman numeral rules
- Works for numbers between 1 and 3999

Alternative Approaches:
1. Recursive solution (more complex)
2. Using a more complex lookup table
3. Multiple pass algorithm
"""

# Example Usage
if __name__ == "__main__":
    solution = Solution()
    
    # Test Case 1: Simple Addition
    roman1 = "III"
    print(f"Roman: {roman1}, Integer: {solution.romanToInt(roman1)}")  # Expected: 3
    
    # Test Case 2: Mixed Addition and Subtraction
    roman2 = "LVIII"
    print(f"Roman: {roman2}, Integer: {solution.romanToInt(roman2)}")  # Expected: 58
    
    # Test Case 3: Complex Subtraction
    roman3 = "MCMXCIV"
    print(f"Roman: {roman3}, Integer: {solution.romanToInt(roman3)}")  # Expected: 1994
    
    # Test Case 4: Single Symbol
    roman4 = "M"
    print(f"Roman: {roman4}, Integer: {solution.romanToInt(roman4)}")  # Expected: 1000