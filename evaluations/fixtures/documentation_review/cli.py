import argparse
from decimal import Decimal


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--amount', type=Decimal, required=True)
    args = parser.parse_args()
    print(f'{args.amount:.2f}')


if __name__ == '__main__':
    main()
