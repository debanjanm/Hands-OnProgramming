"""
LeetCode Problem 1941: Check if All Characters Have Equal Number of Occurrences

1. Problem Statement:
Given a string s, return true if s is a good string, or false otherwise.

A string s is good if all the characters that appear in s have the same number of occurrences 
(i.e., the same frequency).

Example 1:
Input: s = "abacbc"
Output: true
Explanation: The characters that appear in s are 'a', 'b', and 'c'. All characters occur 2 times in s.

Example 2:
Input: s = "aaabb"
Output: false
Explanation: The characters that appear in s are 'a' and 'b'.
'a' occurs 3 times while 'b' occurs 2 times, which is not the same number of times.
"""

from collections import Counter

class Solution:
    def areOccurrencesEqual(self, s: str) -> bool:
        # Count the frequency of each character
        char_count = Counter(s)
        
        # Get the set of all frequencies
        # If all characters have the same frequency, this set will have only one value
        frequencies = set(char_count.values())
        
        # Return true if there's only one unique frequency
        return len(frequencies) == 1
    
    # Alternative implementation without using set
    def areOccurrencesEqual_alt(self, s: str) -> bool:
        char_count = Counter(s)
        
        # Get the first frequency as reference
        reference_freq = next(iter(char_count.values()))
        
        # Check if all other frequencies match the reference
        for freq in char_count.values():
            if freq != reference_freq:
                return False
        
        return True

# 3. Pattern Name:
# Frequency Counter with Uniqueness Check

"""
4. Explanation:
The solution uses a Counter (frequency map) to solve the problem efficiently:

Key Steps:
1. Use Counter to count the occurrences of each character in the string
2. Extract all the frequency values
3. Check if all frequencies are equal by:
   - Main solution: Convert frequencies to a set and check if the set has only one element
   - Alternative solution: Compare each frequency against a reference frequency

For example, given s = "abacbc":
- Counter gives us {'a': 2, 'b': 2, 'c': 2}
- The set of frequencies is {2}
- Since there's only one unique frequency (2), return true

For s = "aaabb":
- Counter gives us {'a': 3, 'b': 2}
- The set of frequencies is {3, 2}
- Since there are two different frequencies, return false

The solution elegantly handles edge cases:
- Empty string: would have no frequencies, but problem states s is non-empty
- Single character string: would have only one frequency, so returns true
- Multiple characters with same frequency: returns true
- Multiple characters with different frequencies: returns false

5. Complexity Analysis:
- Time Complexity: O(n)
  - Creating the Counter requires O(n) time, where n is the length of the string
  - Extracting the set of values is O(k) where k is the number of unique characters
  - Since k ≤ n, the overall time complexity is O(n)
  
- Space Complexity: O(k)
  - The Counter stores at most k entries, one for each unique character
  - The set of frequencies also contains at most k elements
  - In the worst case, all characters are unique, so k = n
  - Therefore, space complexity is O(k) where k ≤ n

Potential optimizations:
- The problem only asks for a boolean result, so we can stop as soon as 
  we find two different frequencies (implemented in the alternative solution)
- If we know the character set is limited (e.g., lowercase English letters),
  we could use a fixed-size array instead of a hash map
"""

# Example Usage
if __name__ == "__main__":
    solution = Solution()
    
    # Test Case 1: All characters occur exactly twice
    s1 = "abacbc"
    print(f"Test Case 1: \"{s1}\" -> {solution.areOccurrencesEqual(s1)}")  # Expected: True
    
    # Test Case 2: Characters have different frequencies
    s2 = "aaabb"
    print(f"Test Case 2: \"{s2}\" -> {solution.areOccurrencesEqual(s2)}")  # Expected: False
    
    # Test Case 3: Single character repeated
    s3 = "mmmm"
    print(f"Test Case 3: \"{s3}\" -> {solution.areOccurrencesEqual(s3)}")  # Expected: True
    
    # Test Case 4: All characters appear once
    s4 = "abcde"
    print(f"Test Case 4: \"{s4}\" -> {solution.areOccurrencesEqual(s4)}")  # Expected: True
    
    # Test Case 5: Mixed frequencies
    s5 = "aabbccddd"
    print(f"Test Case 5: \"{s5}\" -> {solution.areOccurrencesEqual(s5)}")  # Expected: False