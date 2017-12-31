import datetime
import random
from .market import yahoo, coinone, poloniex, upbit, bithumb, premium, bitflyer, korean_stock

code_aliases = {'비트': 'BTC', '빗코': 'BTC', '비트코인': 'BTC', '이더': 'ETH', '이클': 'ETC',
                '리플': 'XRP', 'zcash': 'ZEC', '대시': 'DASH', '리스크': 'LSK', '스팀': 'STEEM',
                '모네로': 'XMR', '스텔라': 'STR', '*': 'ALL', '$': 'USDT', '라코': 'LTC', '젝': 'ZEC',
                '파워레인저': 'POWR', '빗골': 'BTG', '흑트라': 'STRAT', '히오스': 'EOS', '어미새': 'OMG',
                '엠쥐': 'OMG'}


def process_command(args, simple_return=None, processor=None, multiple=False, default_arg='ALL', empty_msg='코드를 입력해주세요'):
    if processor:
        if args:
            args = [code_aliases.get(arg, arg) for arg in args]
        elif not args and default_arg:
            args.append(default_arg)
        else:
            return empty_msg
        return processor(*args)
    elif simple_return:
        return simple_return()
    else:
        return 'Currently in development'


# ({command}, {command process args}, error messsage)
commands = {
    '업빗': {'processor': upbit.get_currency, 'default_arg': 'TOP5'},
    '폴로': {'processor': poloniex.get_currency, 'default_arg': None, 'empty_msg': '폴로: 코드를 입력해주세요 ex) 폴로 doge btc'},
    '코인원': {'processor': coinone.get_currency},
    '빗썸': {'processor': bithumb.get_currency, },
    '빗플': {'processor': bitflyer.get_currency, 'default_arg': 'BTC', },
    '프리미엄': {'simple_return': premium.get},
    '주식': {'processor': korean_stock.get_quote, 'empty_msg': '!주식: 코드를 입력해주세요 ex) !주식 우기투', 'default_arg': None},
    '마켓캡': {'processor': None}
}
command_aliases = {
    '김프': '프리미엄',
    '업비트': '업빗',
}


def functionlist(msg):
    if msg.find('머니봇-ping') >= 0:
        return '머니머니'

    elif msg.find('!시세') >= 0:
        args = msg.split()[1:]
        if args:
            command = args[0]
            leftover = args[1:]
            command_args = commands.get(command) or commands.get(
                command_aliases.get(command))
            if command_args:
                return process_command(leftover, **command_args)
        return 'List of commands: {}'.format(', '.join([c for c in commands]))
