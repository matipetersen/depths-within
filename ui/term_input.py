"""Terminal single-key input helpers for Unix-like systems.

Provides a cross-platform `getch` implementation using termios/tty for
single-character raw input. This is used for interactive console aim mode.
"""
import sys
import tty
import termios


def getch():
    """Read a single character from stdin without echo. Returns as a string."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def getkey():
    """Read key sequences (arrows) and normalize to names.

    Returns:
        single character string for letters/numbers, or
        'UP','DOWN','LEFT','RIGHT' for arrow keys, or other raw sequences.
    """
    ch = getch()
    if ch == '\x1b':
        # possible escape sequence
        seq = ch + sys.stdin.read(2)
        if seq == '\x1b[A':
            return 'UP'
        if seq == '\x1b[B':
            return 'DOWN'
        if seq == '\x1b[C':
            return 'RIGHT'
        if seq == '\x1b[D':
            return 'LEFT'
        return seq
    return ch
