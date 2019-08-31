import sys
from typing import Optional

source = ''
source_index = 0


def get_char() -> Optional[str]:
    if source_index == len(source):
        # byte でなくstrをとりあえず返すので
        # 0として判断できるようなNoneを返す
        return None

    char = source[source_index]
    sourceIndex =+ 1
    return char


def unget_char() -> None:
    source_index -= 1


def main() -> None:
    source = sys.stdin.read() 
    number = int(source)

    print('  .global main')
    print('main:')
    print(f'  movq ${number}, %rax')
    print('  ret')


if __name__ == '__main__':
    main()
