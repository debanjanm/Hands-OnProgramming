"""
LeetCode 914: X of a Kind in a Deck of Cards
===========================================

1. Problem Statement
-------------------
In a deck of cards, each card has an integer written on it.

Return true if and only if you can choose X >= 2 such that it is possible to split the entire deck into 1 or more groups of cards, where:
- Each group has exactly X cards.
- All the cards in each group have the same integer.

2. Code Implementation
--------------------
"""

from collections import Counter
import math

def hasGroupsSizeX(deck):
    """
    :type deck: List[int]
    :rtype: bool
    """
    # Edge case check
    if len(deck) < 2:
        return False
    
    # Count frequency of each card number
    card_counts = Counter(deck)
    
    # Find the greatest common divisor (GCD) of all frequencies
    # If the GCD is >= 2, we can split the deck into groups of that size
    counts = list(card_counts.values())
    
    # Start with the first count
    result = counts[0]
    
    # Calculate the GCD of all counts
    for count in counts[1:]:
        result = math.gcd(result, count)
        # Early termination if GCD becomes 1
        if result == 1:
            return False
    
    # Check if the GCD is at least 2
    return result >= 2

"""
3. Pattern Name
--------------
This problem demonstrates the "Number Theory/GCD (Greatest Common Divisor)" pattern combined with "Frequency Counting".

4. Explanation
------------
The key insight to this problem is understanding that for the deck to be divisible into groups of size X, where each group contains cards with the same number, the frequency of each distinct card number must be divisible by X.

Furthermore, since we want to maximize X (or at least find any valid X), we need to find the greatest common divisor (GCD) of all the frequencies. If the GCD is at least 2, then we can divide the deck into valid groups.

Step-by-step explanation:
1. Count the frequency of each card number using Counter.
2. Extract the frequency values.
3. Calculate the GCD of all these frequencies.
4. If the GCD is greater than or equal to 2, return True; otherwise, return False.

For example, with deck [1,2,3,4,4,3,2,1]:
- Card 1 appears 2 times
- Card 2 appears 2 times
- Card 3 appears 2 times
- Card 4 appears 2 times
- The GCD of [2,2,2,2] is 2, so we can divide the deck into groups of 2

For deck [1,1,1,2,2,2,3,3]:
- Card 1 appears 3 times
- Card 2 appears 3 times
- Card 3 appears 2 times
- The GCD of [3,3,2] is 1, so we can't divide the deck

5. Complexity Analysis
--------------------
Time Complexity: O(n + k log m)
- O(n) to count the frequencies, where n is the size of the deck
- O(k log m) for calculating the GCD of all frequencies, where:
  - k is the number of distinct cards
  - m is the maximum frequency value
  - Computing GCD of two numbers takes O(log m) time using Euclidean algorithm

Space Complexity: O(k)
- We store the frequencies of each distinct card in a Counter
- In the worst case, all cards are distinct, giving O(n) space
- More typically, k << n, where k is the number of distinct cards

"""

# Test cases
test_cases = [
    [1, 2, 3, 4, 4, 3, 2, 1],         # True (can be divided into groups of 2)
    [1, 1, 1, 2, 2, 2, 3, 3],         # False (GCD of frequencies is 1)
    [1, 1, 2, 2, 2, 2],               # True (can be divided into groups of 2)
    [1, 1, 1, 1, 2, 2, 2, 2, 2, 2],   # True (can be divided into groups of 2)
    [1],                               # False (need at least 2 cards)
    [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2], # True (can be divided into groups of 6)
    [1, 1, 1, 2, 2, 2, 3, 3, 3]       # True (can be divided into groups of 3)
]

for i, test in enumerate(test_cases):
    result = hasGroupsSizeX(test)
    print(f"Test {i+1}: {test} -> {result}")