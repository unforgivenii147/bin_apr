#!/data/data/com.termux/files/usr/bin/python
from secrets import randbelow


def show_random_color():
    red = randbelow(256)
    green = randbelow(256)
    blue = randbelow(256)
    print(f"\033[48;2;{red};{green};{blue}m        \033[0m {str(red)} {str(green)} {str(blue)}")


if __name__ == "__main__":
    for i in range(1, randbelow(1000)):
        show_random_color()
