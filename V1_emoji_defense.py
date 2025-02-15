#!/usr/bin/env python3
"""
Unicode Sanitizer for LLM Security
===================================

This module provides a robust Python library to sanitize Unicode text inputs,
aimed at protecting Language Learning Models (LLMs) and other text processing
systems against Unicode-based attacks such as emoji injections and hidden
invisible characters.

Features:
    - Normalizes Unicode text using NFKC to ensure a consistent representation.
    - Splits text into grapheme clusters for accurate handling of combined characters.
    - Filters out disallowed invisible characters (e.g., zero-width spaces) and
      characters from dangerous Unicode categories.
    - Optionally filters out emoji (or selectively allows them) based on configuration.
    - Prevents token explosion attacks by checking the number of tokens per grapheme cluster.
    - Supports custom configuration for disallowed characters and dangerous Unicode categories.

Requirements:
    - Python 3.7+
    - The 'regex' package (install via: pip install regex)
"""

import unicodedata
import regex  # pip install regex
from typing import Callable, Set, Optional, List

# Pre-compiled regex patterns for performance.
# EMOJI_PATTERN: Matches any emoji character based on Unicode properties.
EMOJI_PATTERN = regex.compile(r'\p{Emoji}')
# GRAPHEME_PATTERN: Matches extended grapheme clusters, handling combined characters.
GRAPHEME_PATTERN = regex.compile(r'\X')

# Default set of disallowed/invisible code points.
DEFAULT_DISALLOWED: Set[str] = {
    '\u200B',  # ZERO WIDTH SPACE
    '\u200C',  # ZERO WIDTH NON-JOINER
    '\u200D',  # ZERO WIDTH JOINER
    '\u2060',  # WORD JOINER
    '\uFE0E',  # VARIATION SELECTOR-15 (text presentation)
    '\uFE0F',  # VARIATION SELECTOR-16 (emoji presentation)
}

# Default dangerous Unicode categories (which may indicate non-standard usage).
DEFAULT_DANGEROUS_CATEGORIES: Set[str] = {
    'Co',  # Private use
    'Cn',  # Unassigned
    'Cs',  # Surrogate
    'Cf',  # Format characters
}


def sanitize_unicode(
    text: str,
    tokenizer: Callable[[str], List[str]],
    max_tokens: int = 3,
    replacement: str = '',
    allow_emoji: bool = False,
    strict_mode: bool = True,
    custom_disallowed: Optional[Set[str]] = None,
    custom_dangerous_categories: Optional[Set[str]] = None,
) -> str:
    """
    Sanitizes the provided Unicode text to protect against attacks that abuse
    Unicode's complexity—such as emoji-based injections or hidden invisible characters.

    The sanitization process involves:
      1. Normalizing the text using NFKC to ensure consistent representation.
      2. Splitting the normalized text into grapheme clusters (which accurately
         represents what a user perceives as a single character, including combined symbols).
      3. Examining each grapheme cluster with several security checks:
            - Disallowed invisible characters.
            - Presence of emoji (if allow_emoji is False).
            - Characters belonging to dangerous Unicode categories (when strict_mode is True).
            - Prevention of token explosion (ensuring the cluster doesn’t tokenize into too many tokens).
      4. Replacing any cluster that fails one or more of these checks with the specified replacement string.

    Args:
        text (str): The input Unicode string to sanitize.
        tokenizer (Callable[[str], List[str]]): A function that converts a string into a list of tokens.
            Used to detect potential token explosion vulnerabilities.
        max_tokens (int, optional): Maximum allowed tokens per grapheme cluster.
            Defaults to 3.
        replacement (str, optional): String used to replace disallowed clusters.
            Defaults to an empty string.
        allow_emoji (bool, optional): If False, any grapheme cluster containing an emoji will be replaced.
            If True, emojis are permitted (only filtering out explosive or combined cases if necessary).
            Defaults to False.
        strict_mode (bool, optional): If True, perform additional filtering based on Unicode categories.
            Defaults to True.
        custom_disallowed (Optional[Set[str]], optional): Additional Unicode characters to disallow.
            Defaults to None.
        custom_dangerous_categories (Optional[Set[str]], optional): Additional Unicode categories to filter.
            Defaults to None.

    Returns:
        str: The sanitized version of the input text.

    Example:
        >>> def simple_tokenizer(text: str) -> List[str]:
        ...     return text.split()
        >>> input_text = "Hello 👋 World‍! Hidden\u200B text."
        >>> print(sanitize_unicode(input_text, simple_tokenizer, allow_emoji=False, strict_mode=True))
        "Hello World! Hidden text."
    """
    # Merge default and custom disallowed characters.
    disallowed = DEFAULT_DISALLOWED.copy()
    if custom_disallowed:
        disallowed.update(custom_disallowed)

    # Merge default and custom dangerous Unicode categories.
    dangerous_categories = DEFAULT_DANGEROUS_CATEGORIES.copy()
    if custom_dangerous_categories:
        dangerous_categories.update(custom_dangerous_categories)

    # Step 1: Normalize the text using NFKC (Normalization Form Compatibility Composition)
    normalized_text = unicodedata.normalize('NFKC', text)

    # Step 2: Split the normalized text into grapheme clusters.
    clusters = GRAPHEME_PATTERN.findall(normalized_text)

    sanitized_clusters = []

    for cluster in clusters:
        # Initialize flag to decide if the cluster should be replaced.
        should_replace = False

        # Check 1: Replace if the cluster contains any disallowed (invisible) characters.
        if any(ch in disallowed for ch in cluster):
            should_replace = True

        # Check 2: If emojis are not allowed, replace any cluster containing an emoji.
        elif not allow_emoji and EMOJI_PATTERN.search(cluster):
            should_replace = True

        # Check 3: In strict mode, replace if any character in the cluster belongs to a dangerous Unicode category.
        elif strict_mode and any(unicodedata.category(ch) in dangerous_categories for ch in cluster):
            should_replace = True

        # Check 4: Prevent token explosion by tokenizing the cluster. Replace if token count exceeds max_tokens.
        elif len(tokenizer(cluster)) > max_tokens:
            should_replace = True

        # Append either the replacement or the original cluster.
        sanitized_clusters.append(replacement if should_replace else cluster)

    # Reconstruct and return the sanitized text.
    return ''.join(sanitized_clusters)


def create_basic_tokenizer(max_length: int = 50) -> Callable[[str], List[str]]:
    """
    Creates a basic whitespace-based tokenizer that also truncates tokens
    to a maximum specified length.

    This simple tokenizer splits the input text on whitespace and then truncates
    each token to the defined maximum length. It serves as a demo and testing tool
    for the sanitizer.

    Args:
        max_length (int, optional): Maximum allowed length for any single token.
            Defaults to 50.

    Returns:
        Callable[[str], List[str]]: A function that tokenizes a string into a list of tokens.

    Example:
        >>> tokenizer = create_basic_tokenizer(max_length=10)
        >>> tokenizer("This is a simple tokenization test.")
        ['This', 'is', 'a', 'simple', 'tokenizat']
    """
    def basic_tokenizer(text: str) -> List[str]:
        # Split on whitespace and filter out any empty strings.
        tokens = [token for token in text.split() if token]
        # Truncate each token to the specified maximum length.
        return [token[:max_length] for token in tokens]

    return basic_tokenizer


# Example usage
if __name__ == "__main__":
    # Create a basic tokenizer for demonstration purposes.
    tokenizer = create_basic_tokenizer(max_length=50)

    # Example text containing emojis, invisible characters, and potential token explosion cases.
    test_text = "Hello 👋 World‍! Here's some text with emoji 🌍 and invisible char\u200B!"

    # Sanitize the text.
    sanitized_text = sanitize_unicode(
        text=test_text,
        tokenizer=tokenizer,
        max_tokens=3,
        replacement='',
        allow_emoji=False,
        strict_mode=True
    )

    # Output the original and sanitized texts.
    print("Original text:", test_text)
    print("Sanitized text:", sanitized_text)
