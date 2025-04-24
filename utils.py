ORANGE = "#ff8000"
GREEN = "#00e054"
BLUE = "#40bbf4"
GRAY = "#202831"
DARK_GRAY = "#15191e"

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

def format_number(num):
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}m"
    elif num >= 1_000:
        return f"{num/1_000:.1f}k"
    return str(int(num))
