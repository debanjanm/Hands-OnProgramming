# A plain module - just a .py file with functions/classes/variables in it.

GREETING = "Hello from demo_package.helper"


def shout(text):
    return text.upper()


if __name__ == "__main__":
    # Only runs when this file is executed directly, NOT when imported.
    print("helper.py run directly")
