ORANGE = "#ff8000"
GREEN = "#00e054"
BLUE = "#40bbf4"
GRAY = "#202831"
DARK_GRAY = "#15191e"

star_to_rating = {
    "★": 1,
    "★★": 2,
    "★★★": 3,
    "★★★★": 4,
    "★★★★★": 5,
    "½": 0.5,
    "★½": 1.5,
    "★★½": 2.5,
    "★★★½": 3.5,
    "★★★★½": 4.5,
    None: None
}

def format_with_linebreaks(items, max_line_length=100):
    lines = []
    current_line = ""
    for i, item in enumerate(items):
        is_last = (i == len(items) - 1)
        addition = item if is_last else item + ", "
        if len(current_line) + len(addition) > max_line_length:
            lines.append(current_line.rstrip())
            current_line = ""
        current_line += addition
    if current_line:
        lines.append(current_line.rstrip())
    return "<br>".join(lines)
