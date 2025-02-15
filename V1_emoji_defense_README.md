# Unicode Sanitizer for LLM Security

A robust Python library for sanitizing Unicode text input to protect Language Learning Models (LLMs) and other text processing systems against emoji-based attacks and other Unicode-based security vulnerabilities.

## Key Features

- 🔒 Protection against emoji-based attacks
- 🧹 Unicode normalization (NFKC)
- 🎯 Grapheme cluster analysis
- ⚡ Token explosion prevention
- 🛠️ Configurable security levels
- 📝 Custom character and category filtering

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Basic Example](#basic-example)
- [API Reference](#api-reference)
  - [sanitize_unicode](#sanitize_unicode)
  - [create_basic_tokenizer](#create_basic_tokenizer)
- [Configuration Options](#configuration-options)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [Acknowledgements](#acknowledgements)

---

## Features

- **Unicode Normalization:** Standardizes text using NFKC to ensure consistent representation.
- **Grapheme Cluster Analysis:** Splits text into grapheme clusters so that complex characters (such as emojis and combined diacritics) are handled correctly.
- **Disallowed Character Filtering:** Removes disallowed or invisible characters (e.g., zero-width spaces, joiners, and variation selectors).
- **Emoji Filtering:** Optionally filters out emojis to mitigate potential injection attacks.
- **Token Explosion Prevention:** Uses a customizable tokenizer to check for excessive tokenization of a single grapheme cluster.
- **Customizable:** Easily extend or override default disallowed characters and dangerous Unicode categories.
- **Pluggable Tokenizer:** Supports integration with different tokenizers tailored to your use case.

---

## Installation

Ensure you have Python 3.7 or above installed. Then, install the required dependency:

```bash
pip install regex
```

---

## Usage

### Basic Example

Below is an example demonstrating how to use the sanitizer to clean a text input containing emojis and invisible characters.

```python
from unicode_sanitizer import sanitize_unicode, create_basic_tokenizer

# Create a basic tokenizer that splits text on whitespace and truncates tokens to 50 characters.
tokenizer = create_basic_tokenizer(max_length=50)

# Example input: text with an emoji and an invisible character (zero-width space).
input_text = "Hello 👋 World‍! Here's some text with emoji 🌍 and an invisible char\u200B!"

# Sanitize the text:
# - max_tokens: Maximum allowed tokens per grapheme cluster is set to 3.
# - replacement: Disallowed clusters will be replaced with an empty string.
# - allow_emoji: Set to False, so any emoji will be removed.
# - strict_mode: Enables filtering based on dangerous Unicode categories.
clean_text = sanitize_unicode(
    text=input_text,
    tokenizer=tokenizer,
    max_tokens=3,
    replacement='',
    allow_emoji=False,
    strict_mode=True
)

print("Original:", input_text)
print("Sanitized:", clean_text)
```

Running the above example will display the original text and its sanitized version.

---

## API Reference

### `sanitize_unicode`

**Signature:**

```python
sanitize_unicode(
    text: str,
    tokenizer: Callable[[str], List[str]],
    max_tokens: int = 3,
    replacement: str = '',
    allow_emoji: bool = False,
    strict_mode: bool = True,
    custom_disallowed: Optional[Set[str]] = None,
    custom_dangerous_categories: Optional[Set[str]] = None
) -> str
```

**Description:**

Sanitizes the input Unicode text by:

1. Normalizing the text using NFKC to ensure consistency.
2. Splitting the normalized text into grapheme clusters.
3. Applying a series of checks on each grapheme cluster:
   - **Disallowed Characters:** Replaces clusters containing any disallowed invisible characters.
   - **Emoji Filtering:** If `allow_emoji` is `False`, any cluster containing an emoji is replaced.
   - **Strict Mode Checks:** In `strict_mode`, clusters containing characters from dangerous Unicode categories are replaced.
   - **Token Explosion Prevention:** Clusters that tokenize into more than `max_tokens` are replaced.
4. Reconstructing the text from the approved grapheme clusters.

**Parameters:**

- **text (str):** Input Unicode string to sanitize.
- **tokenizer (Callable[[str], List[str]]):** A function that tokenizes a string into a list of tokens. This is used to detect token explosion vulnerabilities.
- **max_tokens (int, optional):** Maximum allowed tokens per grapheme cluster (default is 3).
- **replacement (str, optional):** String used to replace any disallowed grapheme cluster (default is an empty string).
- **allow_emoji (bool, optional):** If `False`, any grapheme cluster containing an emoji will be replaced (default is `False`).
- **strict_mode (bool, optional):** If `True`, additional filtering based on Unicode categories is applied (default is `True`).
- **custom_disallowed (Optional[Set[str]], optional):** Additional Unicode characters to disallow.
- **custom_dangerous_categories (Optional[Set[str]], optional):** Additional dangerous Unicode categories to filter.

**Returns:**

- **str:** The sanitized text.

---

### `create_basic_tokenizer`

**Signature:**

```python
create_basic_tokenizer(max_length: int = 50) -> Callable[[str], List[str]]
```

**Description:**

Creates a simple whitespace-based tokenizer that splits input text into tokens and truncates each token to a maximum specified length.

**Parameters:**

- **max_length (int, optional):** Maximum allowed length for any single token (default is 50).

**Returns:**

- **Callable[[str], List[str]]:** A function that tokenizes a string into a list of tokens.

---

## Configuration Options

- **max_tokens:** Defines the maximum allowed token count per grapheme cluster. This prevents potential token explosion attacks.
- **allow_emoji:** Determines whether emojis are permitted in the sanitized output. Set to `False` by default to enhance security.
- **strict_mode:** When enabled, applies additional checks based on Unicode categories to catch less obvious vulnerabilities.
- **custom_disallowed / custom_dangerous_categories:** Extend or override the default lists of characters or categories that are deemed unsafe.

---

## Contributing

Contributions are welcome! If you'd like to help improve this library:

1. **Fork the repository.**
2. **Create a feature branch:**  
   ```bash
   git checkout -b my-new-feature
   ```
3. **Implement your changes:** Include new tests and update documentation as needed.
4. **Run tests:** Ensure your changes don’t break existing functionality.
5. **Submit a pull request:** Provide a detailed description of your modifications.

---

## License

This project is licensed under the APACHE License. See the [LICENSE](LICENSE) file for details.

---

## Contact

For security-related issues, general inquiries, or contributions, please open an issue on GitHub or contact [renee@freedomfamilyconsulting.ca].

---

## Acknowledgements

- Inspired by emerging discussions on emoji-based and Unicode injection attacks.
- Thanks to the cybersecurity and LLM communities for ongoing insights into Unicode vulnerabilities.
- Special thanks to the authors of related research (e.g., Paul Butler’s “Smuggling arbitrary data through an emoji” and the Emoji Attack paper) that influenced this work.

---

Feel free to adapt this README to your project's needs.