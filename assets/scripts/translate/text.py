import re
from typing import Dict, List, Tuple

from nltk.tokenize import sent_tokenize

SPECIAL_PATTERNS = {
    r"\*\*\*(.*?)\*\*\*": ("<BOLD_ITALIC>$1</BOLD_ITALIC>", "**$1**"),  # Bold and italic
    r"\*\*(.*?)\*\*": ("<BOLD>$1</BOLD>", "**$1**"),                    # Bold
    r"\*(.*?)\*": ("<ITALIC>$1</ITALIC>", "*$1*"),                      # Italic
    r"`([^`]+?)`": ("<CODE>$1</CODE>", "`$1`"),                         # Inline code
    r"```([\s\S]*?)```": ("<PRE>$1</PRE>", "```$1```"),                 # Code block
    r"#{6}\s+(.+?)(?:\n|$)": ("<H6>$1</H6>", "###### $1"),              # H6 header
    r"#{5}\s+(.+?)(?:\n|$)": ("<H5>$1</H5>", "##### $1"),               # H5 header
    r"#{4}\s+(.+?)(?:\n|$)": ("<H4>$1</H4>", "#### $1"),                # H4 header
    r"#{3}\s+(.+?)(?:\n|$)": ("<H3>$1</H3>", "### $1"),                 # H3 header
    r"#{2}\s+(.+?)(?:\n|$)": ("<H2>$1</H2>", "## $1"),                  # H2 header
    r"#\s+(.+?)(?:\n|$)": ("<H1>$1</H1>", "# $1"),                      # H1 header
    r"^\s*[-*+]\s+(.+?)(?=\n|$)": ("<LI>$1</LI>", "- $1"),              # Unordered list item
    r"^\s*\d+\.\s+(.+?)(?=\n|$)": ("<LI>$1</LI>", "1. $1"),             # Ordered list item
    r"\[(.+?)\]\((.+?)\)": ("<LINK text='$1' url='$2'>", "[$1]($2)"),   # Links
    r"!\[(.+?)\]\((.+?)\)": ("<IMG alt='$1' src='$2'>", "![$1]($2)"),   # Images
    r">\s+(.+?)(?=\n|$)": ("<QUOTE>$1</QUOTE>", "> $1"),                # Blockquote
    r"\n\n": ("<PARA>", "\n\n"),                                        # Paragraph break
    r"\n": ("<NL>", "\n"),                                              # Single newline
}

def preprocess_text(text: str) -> Tuple[str, Dict[str, str], List[Tuple[str, str]]]:
    if not isinstance(text, str) or not text.strip():
        return text, {}, []

    tag_map = {}
    counter = 0
    structure = []  # List of (type, content) tuples: type can be 'text', 'tag', etc.

    # Process Markdown patterns
    for pattern, tag_template in SPECIAL_PATTERNS.items():
        def replace_match(match):
            nonlocal counter
            unique_tag = f"<TAG{counter}>"
            content = match.group(1) if "$1" in tag_template else match.group(0)
            tag_map[unique_tag] = tag_template.replace("$1", content) if "$1" in tag_template else tag_template
            counter += 1
            return unique_tag
        
        text = re.sub(pattern, replace_match, text, flags=re.DOTALL)

    # Split into sentences while preserving tags
    sentences = []
    current_sentence = ""
    for char in text:
        if (char in "<>"):
            if current_sentence:
                sentences.extend(sent_tokenize(current_sentence))
                current_sentence = ""
            structure.append(("tag", char))
        else:
            current_sentence += char
            structure.append(("text", char))
    if current_sentence:
        sentences.extend(sent_tokenize(current_sentence))

    return " ".join(sentences), tag_map, structure

def postprocess_text(translated_sentences: List[str], placeholder_map: Dict[str, str], structure: List[Tuple[str, str]]) -> str:
    if not translated_sentences or not structure:
        return ""

    result = ""
    sentence_idx = 0
    char_idx = 0
    current_sentence = translated_sentences[sentence_idx] if translated_sentences else ""

    for item_type, content in structure:
        if item_type == "placeholder":
            # Replace placeholder with original Markdown
            tag_content = placeholder_map.get(content, content)
            for _, (tag, original_pattern) in SPECIAL_PATTERNS.items():
                if tag in tag_content:
                    if "<LINK" in tag_content or "<IMG" in tag_content:
                        # Extract text and url/src from the placeholder
                        text_match = re.search(r"text='([^']+)'", tag_content)
                        url_match = re.search(r"(url|src)='([^']+)'", tag_content)
                        text = text_match.group(1) if text_match else ""
                        url = url_match.group(2) if url_match else ""
                        result += original_pattern.replace("$1", text).replace("$2", url)
                    else:
                        content_match = re.search(r">(.+?)<", tag_content)
                        content_text = content_match.group(1) if content_match else ""
                        result += original_pattern.replace("$1", content_text)
                    break
            else:
                result += tag_content  # Fallback if no pattern matches
        elif item_type == "text":
            if sentence_idx < len(translated_sentences) and char_idx < len(current_sentence):
                result += current_sentence[char_idx]
                char_idx += 1
            if char_idx >= len(current_sentence) and sentence_idx < len(translated_sentences) - 1:
                sentence_idx += 1
                char_idx = 0
                current_sentence = translated_sentences[sentence_idx]

    return result.strip()
