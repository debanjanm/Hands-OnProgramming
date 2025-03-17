"""
LeetCode 804: Unique Morse Code Words

1. Problem Statement:
International Morse Code defines a standard encoding where each letter is mapped to a series of dots and dashes, as follows:
- 'a' maps to ".-",
- 'b' maps to "-...",
- 'c' maps to "-.-.", etc.

For convenience, the full table for the 26 letters of the English alphabet is given below:
[".-","-...","-.-.","-..",".","..-.","--.","....","..",".---","-.-",".-..","--","-.","---",".--.","--.-",".-.","...","-","..-","...-",".--","-..-","-.--","--.."]

Given an array of strings words where each word can be written as a concatenation of the Morse code of each letter, return the number of different transformations among all words we have.

2. Code Implementation:
"""

def unique_morse_representations(words):
    """
    Find the number of unique Morse code transformations for a list of words.
    
    Args:
        words (List[str]): List of words
        
    Returns:
        int: Number of unique Morse code transformations
    """
    # Morse code mapping for each letter (a-z)
    morse_codes = [".-","-...","-.-.","-..",".","..-.","--.","....","..",".---","-.-",".-..","--",
                   "-.","---",".--.","--.-",".-.","...","-","..-","...-",".--","-..-","-.--","--.."]
    
    # Set to store unique Morse code representations
    unique_transformations = set()
    
    # Process each word
    for word in words:
        # Convert each letter to Morse code and concatenate
        morse_representation = ""
        for char in word:
            # Convert character to index (0-25) and look up Morse code
            morse_representation += morse_codes[ord(char) - ord('a')]
        
        # Add the Morse representation to the set
        unique_transformations.add(morse_representation)
    
    # Return the number of unique transformations
    return len(unique_transformations)

"""
3. Pattern Name:
Set / Hash Set

4. Explanation:
This problem asks us to convert each word into its Morse code representation and count the number of unique representations.

The approach:
1. Define a list of Morse code representations for each letter of the alphabet (a-z).

2. Initialize a set to track unique Morse code transformations.
   - We use a set because it automatically handles duplicates and provides O(1) lookup time.

3. For each word in the input list:
   - Convert each character to its corresponding Morse code representation
   - Concatenate these representations to form the Morse code for the entire word
   - Add this representation to our set of unique transformations

4. Return the size of the set, which represents the number of unique Morse code transformations.

This approach is efficient because:
- We only need to process each character in each word once
- The set automatically handles deduplication
- Converting a character to its Morse code representation is a simple lookup operation

The solution correctly handles all edge cases:
- Empty words (would result in empty Morse code strings)
- Words with repeated letters (Morse code is simply concatenated)
- Different words that result in the same Morse code (counted only once)

5. Complexity Analysis:
Time Complexity: O(n), where n is the total number of characters across all words
- We process each character in each word exactly once
- Converting a character to its Morse code representation is O(1)
- Adding to a set is O(1) on average

Space Complexity: O(n)
- In the worst case, every word has a unique Morse code representation
- The set would then contain one entry for each word
- Each entry could be up to the length of the original word (in Morse code)
- Therefore, the space complexity is proportional to the total input size
"""

# Example test cases
if __name__ == "__main__":
    # Example 1
    words = ["gin", "zen", "gig", "msg"]
    print(unique_morse_representations(words))  # Expected output: 2
    # Explanation: The transformations are:
    # "gin" -> "--...-."
    # "zen" -> "--...-."
    # "gig" -> "--...--."
    # "msg" -> "--...--."
    
    # Example 2
    words = ["a"]
    print(unique_morse_representations(words))  # Expected output: 1