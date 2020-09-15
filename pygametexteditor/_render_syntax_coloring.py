from typing import List, Dict, Tuple


def get_syntax_coloring_dicts(self) -> List[List[Dict]]:
    """
    Converts the text in the editor based on the line_String_array into a list of lists of dicts.
    Every line is one sublist which contains different dicts based on it's contents.

    We create a dict for every part of the line and include which letters are contained, the type and the color.
    So far implemented:
    - comments
    - single-quoted Strings
    - hashtags in quotes
    TODO:
    - double-quoted Strings
    - keywords
    - standalone - numbers
    """

    # Identify render-blocks
    # For now, we recreate all of it every frame
    rendering_list = []
    for line in self.line_String_array:

        # Split at first comment outside of a string
        text, comments = self.search_for_comment(line)

        # Split on quotes into quoted and unquoted strings
        list_of_dicts = self.search_for_quotes(text)

        # TODO: SPLIT ON ALL OTHER THINGS, THEN CHECK FOR KEYWORDS AND STANDALONE NUMBERS!

        if comments != "":  # comment-string not empty, insert as last block.
            list_of_dicts.append({'chars': comments, 'type': 'comment', 'color': self.textColor_comments})

        rendering_list.append(list_of_dicts)
    return rendering_list


def get_single_color_dicts(self) -> List[List[Dict]]:
    """
    Converts the text in the editor based on the line_String_array into a list of lists of dicts.
    Every line is one sublist.
    Since only one color is being applied, we create a list with one dict per line.
    """
    rendering_list = []
    for line in self.line_String_array:
        # appends a single-item list
        rendering_list.append([{'chars': line, 'type': 'normal', 'color': self.textColor}])

    return rendering_list


def find_nth(haystack, needle, n) -> int:
    """
    Finds the nth occurance of a string (=needle) in a string (=haystack) and returns its index.
    Returns -1 if none could be found.
    """
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start


def search_for_quotes(self, sstring) -> List[Dict]:  # TODO: ADAPT FOR DOUBLE QUOTES
    """
    Searches for tuples of quotes in the supplied searchable string.
    Returns a list of dicts describing the contents by the attributes:
    - chars (actual text)
    - type (normal / quoted)
    - color (text-coloring)
    """

    quotes = self.get_quote_tuples(sstring)

    dicts = []
    offset = 0
    for tp in quotes:
        tp0 = tp[0] - offset  # adjusted start
        tp1 = tp[1] - offset + 1  # adjusted end

        # append unqoted-area
        dicts.append({'chars': sstring[0:tp0], 'type': 'normal', 'color': self.textColor})
        # append quoted-area
        dicts.append({'chars': sstring[tp0:tp1], 'type': 'quoted', 'color': self.textColor_quotes})

        sstring = sstring[tp1:]  # reduce searchable_string to the rest
        offset += tp1  # add to existing offset

    if len(sstring) > 0:  # append rest as un-quoted area -> if there is some left over
        dicts.append({'chars': sstring, 'type': 'normal', 'color': self.textColor})

    return dicts


def search_for_comment(self, text) -> Tuple[str, str]:
    """
    Searches for the first comment outside of quotes.
    Returns the text and the quotes as a tuple
    :returns (text, comments)
    """
    quotes = self.get_quote_tuples(text)
    hashtags = self.get_hashtags(text)
    sep_at = -1
    for c in hashtags:  # identify first comment outside of quotes.
        outside = True
        for tp in quotes:
            if tp[0] < c < tp[1]:
                outside = False

        if outside:  # first one outside found.
            sep_at = c
            break

    if sep_at > 0:  # found a comment outside of quotes
        return text[:sep_at], text[sep_at:]  # text, comments
    else:
        return text, ""


def get_quote_tuples(self, text) -> List[Tuple[int, int]]:
    """
    Searches for the quoted text within a text, single and double quotes.
    Returns a list of tuples symbolizing the start and end indizies of the quoted area.
    If there is no closing quote for a starting quote, the index for the end is set to the last character of the text.
    Returns an empty list of no quotes are found.
    :returns [(start_index, end_index)]
    """
    quotes = []
    cont = 0
    for i, char in enumerate(text):
        if i > cont:  # only take a look at those necessary
            # SINGLE and DOUBLE Quote
            if char in ("'", '"'):
                start = i
                end = text.find(char, i+1)  # find closing quote after starting quote
                if end == -1:  # no closing quote found
                    quotes.append((start, len(text)))
                    break
                else:
                    quotes.append((start, end))
                    cont = end  # continue after end
    return quotes


def get_hashtags(self, text) -> List[int]:
    """
    Searches a text for hashtags and returns a list of the found hashtag's indizes.
    Returns an empty list if none are found.
    """
    comments = []
    for j in range(1, 1000, 1):
        index = find_nth(text, "#", j)
        if index == -1:  # no more to be found, stop searching
            break
        comments.append(index)
    return comments

