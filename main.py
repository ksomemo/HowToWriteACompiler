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
            print(f" '{token.value}'", end='')
        elif char in [' ', '\t', '\n']:
            continue
        elif char in [';', '+', '-', '*', '/']:
            token = Token('punct', char)
            tokens.append(token)
            print(f" '{token.value}'", end='')
        else:
            raise Exception(f"tokenizer: Invalid char: '{char}'")
            # golang panic: output exit status 2 to stderr
            # but, $? is 1

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
    """golang のstruct に合わせてdefault 設定
    """
    kind: str # "intliteral", "unary"
    intval: int = 0   # for intliteral
    operator: str = '' # "-", "+", ...
    # https://www.python.org/dev/peps/pep-0484/#forward-references
    operand: Optional['Expr'] = None # for unary expr
    left: Optional['Expr'] = None # for binary expr
    right: Optional['Expr'] = None # for binary expr

def parse_unary_expr() -> Optional[Expr]:
    token = get_token()

    if token.kind == 'intliteral':
        intval = int(token.value)
        return Expr('intliteral', intval=intval)
    elif token.kind == 'punct':
        return Expr('unary',
                    operator=token.value,
                    operand=parse_unary_expr())
    else:
        raise Exception('Unexpected token')


def parse() -> Expr:
    expr = parse_unary_expr()

    while True:
        token = get_token()
        if token is None or token.value == ';':
            return expr

        if token.value in ['+', '-', '*', '/']:
            return Expr('binary',
                        operator=token.value,
                        left=expr,
                        right=parse_unary_expr())
        else:
            raise Exception(f'unexpected token: {token.value}')


def generate_expr(expr: Expr) -> None:
    if expr.kind == 'intliteral':
        print(f'  movq ${expr.intval}, %rax')
    elif expr.kind == 'unary':
        if expr.operator == '-':
            print(f'  movq $-{expr.operand.intval}, %rax')
        elif '+':
            print(f'  movq ${expr.operand.intval}, %rax')
        else:
            raise Exception(f'generator: Unknown unary operator: {expr.operator}')
    elif expr.kind == 'binary':
        print(f'  movq ${expr.left.intval}, %rax')
        print(f'  movq ${expr.right.intval}, %rcx')

        if expr.operator == '+':
            print('  addq %rcx, %rax')
        elif expr.operator == '-':
            print('  subq %rcx, %rax')
        elif expr.operator == '*':
            print('  imulq %rcx, %rax')
        elif expr.operator == '/':
            print('  movq $0, %rdx')
            print('  idiv %rcx')
        else:
            raise Exception(f'generator: Unknown binary operator: {expr.operator}')
    else:
        raise Exception(f'generator: Unknown expr.kind: {expr.kind}')


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
