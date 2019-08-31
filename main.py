import sys


def main():
    source = sys.stdin.read() 
    number = int(source)

    print('  .global main')
    print('main:')
    print(f'  movq ${number}, %rax')
    print('  ret')


if __name__ == '__main__':
    main()
