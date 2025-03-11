"""
LeetCode 205: Isomorphic Strings

1. Problem Statement:
Given two strings s and t, determine if they are isomorphic.

Two strings s and t are isomorphic if the characters in s can be replaced to get t.

All occurrences of a character must be replaced with another character while preserving the order of characters.
No two characters may map to the same character, but a character may map to itself.

2. Code Implementation:
"""

def is_isomorphic(s, t):
    """
    Determine if two strings are isomorphic.
    
    Args:
        s (str): First string
        t (str): Second string
        
    Returns:
        bool: True if the strings are isomorphic, False otherwise
    """
    # If lengths are different, they can't be isomorphic
    if len(s) != len(t):
        return False
    
    # Create dictionaries to track character mappings in both directions
    s_to_t = {}
    t_to_s = {}
    
    # Iterate through both strings simultaneously
    for char_s, char_t in zip(s, t):
        # Check if s_char is already mapped
        if char_s in s_to_t:
            # If mapped to a different character, not isomorphic
            if s_to_t[char_s] != char_t:
                return False
        # Check if t_char is already mapped to a different s_char
        elif char_t in t_to_s:
            # This means char_s is new, but char_t already has a mapping
            return False
        else:
            # Create new mapping in both directions
            s_to_t[char_s] = char_t
            t_to_s[char_t] = char_s
    
    return True

"""
3. Pattern Name:
Character Mapping / Hash Table

4. Explanation:
This problem requires us to determine if two strings have the same pattern of characters,
regardless of what the actual characters are.

Two strings are isomorphic if:
1. Each character in the first string can be uniquely mapped to a character in the second string
2. The pattern of character repetitions is identical in both strings
3. No two different characters in the first string map to the same character in the second string

The approach:
1. We use two hash maps to track character mappings in both directions:
   - s_to_t: Maps characters from string s to string t
   - t_to_s: Maps characters from string t to string s
   
2. We iterate through both strings simultaneously, checking for each character pair:
   - If char_s is already mapped, ensure it maps to the current char_t
   - If char_t is already mapped, ensure it maps to the current char_s
   - Otherwise, create a new mapping in both directions
   
3. If at any point we find inconsistent mappings, we return False

By tracking mappings in both directions, we ensure the bijective property:
- No two characters in s map to the same character in t
- No two characters in t map to the same character in s

This approach handles all edge cases:
- Strings of different lengths (checked at the beginning)
- Characters mapping to themselves (allowed)
- Characters with multiple occurrences (must maintain consistent mapping)

5. Complexity Analysis:
Time Complexity: O(n)
- We iterate through both strings once, where n is the length of the strings.
- Each operation within the loop (dictionary lookups, insertions) is O(1) on average.
- Therefore, the overall time complexity is linear with respect to the input length.

Space Complexity: O(k)
- We use two dictionaries to store character mappings.
- In the worst case, each dictionary can store up to k entries, where k is the size of the character set.
- Since the problem typically deals with ASCII or Unicode characters, k is a constant.
- Therefore, the space complexity is O(k), which can be considered O(1) if we assume a fixed character set.
"""

# Example test cases
if __name__ == "__main__":
    # Example 1
    s = "egg"
    t = "add"
    print(is_isomorphic(s, t))  # Expected output: True
    
    # Example 2
    s = "foo"
    t = "bar"
    print(is_isomorphic(s, t))  # Expected output: False
    
    # Example 3
    s = "paper"
    t = "title"
    print(is_isomorphic(s, t))  # Expected output: True
    
    # Example 4
    s = "badc"
    t = "baba"
    print(is_isomorphic(s, t))  # Expected output: False