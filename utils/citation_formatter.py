import re

def format_citations(text: str) -> str:
    """
    Finds citations in the format and
    converts them into a more user-friendly format for display.
    """
    # Regex pattern to find citations like [source.pdf, page 12]
    pattern = r'\+), page (\d+)\]'

    # This example converts it to a simple footnote-like format for display
    formatted_text = re.sub(pattern, r' (Source: \1, Page: \2)', text)

    return formatted_text