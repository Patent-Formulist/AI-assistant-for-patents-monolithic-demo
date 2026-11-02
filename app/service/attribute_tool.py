import re

from core import logger

logger = logger.get_logger(__name__)


class AttributeToolService:
    @staticmethod
    async def attribute_list_generator(text: str) -> list[str]:
        """Extracts items from numbered and bulleted lists.

        Returns only list items, ignores regular text.
        """
        if text is None:
            logger.warning("attribute_list_generator received None instead of text")
            return []

        if not isinstance(text, str):
            logger.warning(f"attribute_list_generator received {type(text)} instead of str")
            try:
                text = str(text)
            except Exception:
                return []

        result = []  # List to store extracted items

        for line in text.split("\n"):
            line = line.strip()  # Remove leading/trailing whitespace
            if not line:  # Skip empty lines
                continue

            # Check for numbered list items (1., 2), a., b), etc.)
            if re.match(r"^(\d+|[a-zA-Zа-яА-Я])[.)]\s+", line):  # Numbered list pattern
                match = re.match(r"^(\d+|[a-zA-Zа-яА-Я])[.)]\s+(.*)", line)
                result.append(match.group(2))  # Add the text content after number/letter
            # Check for bulleted list items (•, -, *, etc.)
            elif re.match(r"^[•\-*]\s+", line):  # Bulleted list pattern
                match = re.match(r"^[•\-*]\s+(.*)", line)
                result.append(match.group(1))  # Add the text content after bullet

        return result

    @staticmethod
    def statistics_dict_generator(text: str) -> dict[int, str]:
        """Parses a text block with numbered items and their signs (+/-) into a dictionary.

        The input text should have lines in format "text: +" or "text: -".
        Returns a dictionary where keys are line numbers and values are the signs.
        """
        result = {}  # Dictionary to store the results (number: sign)
        current_number, current_sign = 0, None  # Track current item number and its sign
        # Process each line in the input text
        for line in text.split("\n"):
            line = line.strip()  # Remove leading/trailing whitespace
            if not line:  # Skip empty lines
                continue
            # Check if line matches the pattern "text: +" or "text: -"
            # group(1) = text before colon, group(2) = the + or - sign
            match = re.match(r"^(.+?):\s*([-+])", line)
            if match:
                if current_number != 0:  # If we already had a previous item, save it to results
                    result[current_number] = current_sign
                current_number += 1  # Increment item number
                current_sign = match.group(2)  # Store the sign (+ or -)
        if current_number != 0:  # Save the last item if it exists
            result[current_number] = current_sign
        return result
