"""
LeetCode 1408: String Matching in an Array

1. Problem Statement:
Given an array of string words, return all strings in words that are substrings of another word in the array.

A substring is a contiguous sequence of characters within a string.

2. Code Implementation:
"""

def string_matching(words):
    """
    Find all strings that are substrings of another string in the array.
    
    Args:
        words (List[str]): List of strings
        
    Returns:
        List[str]: List of strings that are substrings of another string in the array
    """
    # Result list to store substrings
    result = []
    
    # Check each word to see if it's a substring of any other word
    for i, word in enumerate(words):
        for j, other_word in enumerate(words):
            # Skip comparing a word with itself
            if i != j and word in other_word:
                # If word is a substring of other_word, add it to result and break
                result.append(word)
                break
    
    return result

"""
3. Pattern Name:
String Comparison / Brute Force Search

4. Explanation:
This problem asks us to find all strings in an array that are substrings of any other string in the array.

The approach:
1. We iterate through each word in the array.

2. For each word, we compare it with every other word in the array:
   - If the current word is a substring of another word (and not the same word), 
     we add it to our result list.
   - We use the 'in' operator which checks if one string is a substring of another.
   - Once we find that a word is a substring, we break out of the inner loop 
     to avoid duplicate additions.

3. After checking all words, we return the result list.

This approach uses a brute force comparison, which is appropriate for this problem given:
- The typical constraints (array length ≤ 100, word length ≤ 30)
- The straightforward nature of substring testing in Python

The solution correctly handles edge cases:
- Empty strings (would be substrings of any string)
- Identical strings (avoided by skipping self-comparison)
- Words that appear as substrings in multiple other words (counted only once)

Alternative approaches:
- Sort the array by length first, so shorter strings (potential substrings) are checked against longer strings.
- Use a trie data structure for more efficient substring checking in larger datasets.

5. Complexity Analysis:
Time Complexity: O(n²·m), where:
- n is the number of words in the array
- m is the maximum length of any word
- We compare each word with every other word: O(n²)
- Each comparison (substring check) takes O(m) time
- Therefore, the overall time complexity is O(n²·m)

Space Complexity: O(k), where k is the number of words that are substrings
- We only store the words that are substrings of other words
- In the worst case, all words except the longest one could be substrings, making it O(n)
"""

# Example test cases
if __name__ == "__main__":
    # Example 1
    words = ["mass", "as", "hero", "superhero"]
    print(string_matching(words))  # Expected output: ["as", "hero"]
    
    # Example 2
    words = ["leetcode", "et", "code"]
    print(string_matching(words))  # Expected output: ["et", "code"]
    
    # Example 3
    words = ["blue", "green", "bu"]
    print(string_matching(words))  # Expected output: []
    
    # Example 4
    words = ["a", "abc", "bc", "d"]
    print(string_matching(words))  # Expected output: ["a", "bc"]