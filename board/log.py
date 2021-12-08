"""
Basic logging helper.
"""
from board.display import oled

def logger(statement: str) -> None:
    print(statement)
    oled.write_text(statement)
