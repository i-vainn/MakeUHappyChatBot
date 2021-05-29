import argparse
from worker import Worker

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--telegram_token', required=True, help='Token for chat-bot access.')
    args = parser.parse_args()
    Worker(args.telegram_token).work()