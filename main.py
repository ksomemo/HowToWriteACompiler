import sys
import dataclasses
import string
from typing import Optional, List

source = ''
source_index = 0
tokens = []
token_index = 0


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


def get_token() -> Token:
    global tokens, token_index
    if token_index == len(tokens):
        return None

    token = tokens[token_index]
    token_index += 1
    return token


@dataclasses.dataclass
class Expr:
    kind: str # "intliteral"
    intval: int # for intliteral


def parse_unary_expr() -> Expr:
    token = get_token()

    intval = int(token.value)
    expr = Expr('intliteral', intval)
    return expr


def parse() -> Expr:
    expr = parse_unary_expr()
    return expr


def generate_expr(expr: Expr) -> None:
    print(f'  movq ${expr.intval}, %rax')


def generate_code(expr: Expr) -> None:
    print('  .global main')
    print('main:')
    generate_expr(expr)
    print('  ret')


def main() -> None:
    global source, tokens
    source = sys.stdin.read() 
    tokens = tokenize()
    expr = parse()
    generate_code(expr)


if __name__ == '__main__':
    main()
