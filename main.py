import sys
import dataclasses
import string
from typing import Optional, List

source = ''
source_index = 0


def get_char() -> Optional[str]:
    global source, source_index
    if source_index == len(source):
        # byte でなくstrをとりあえず返すので
        # 0として判断できるようなNoneを返す
        return None

    char = source[source_index]
    source_index += 1 
    return char


def unget_char() -> None:
    global source_index
    source_index -= 1


@dataclasses.dataclass
class Token:
    kind: str # "intliteral", "punct"
    value: str

def read_number(char: str) -> str:
    number = [char]
    while True:
        char = get_char()
        if char is None:
            break

        if '0' <= char and char <= '9':
            number.append(char)
        else:
            unget_char()
            break

    return ''.join(number)


def tokenize() -> List[Token]:
    tokens = []
    print('# Tokens : ', end='')

    while True:
        char = get_char()
        if char is None:
            break

        if char in string.digits:
            intliteral = read_number(char)
            token = Token('intliteral', intliteral)
            tokens.append(token)
            print(f" '{token.value}'")
        elif char in [' ', '\t', '\n']:
            continue
        elif char == ';':
            token = Token('punct', char)
            tokens.append(token)
            print(f" '{token.value}'")
        else:
            message = f"tokenizer: Invalid char: '{char}'"
            print(message, file=sys.stderr)
            # golang panic: output exit status 2 to stderr
            # but, $? is 1
            sys.exit(1)

    print()
    return tokens


def main() -> None:
    global source
    source = sys.stdin.read() 
    tokens = tokenize()
    token0 = tokens[0]
    number = int(token0.value)

    print('  .global main')
    print('main:')
    print(f'  movq ${number}, %rax')
    print('  ret')


if __name__ == '__main__':
    main()
