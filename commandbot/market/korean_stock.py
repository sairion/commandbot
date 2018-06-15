# -*- coding: utf-8 -*-
import requests
import urllib.parse
from requests_html import HTMLSession
from bs4 import BeautifulSoup


code_cache = {
    '우리기술투자': 'KOREA-A041190',
    '카카오': 'KOREA-A035720',
    'SBI인베스트먼트': 'KOREA-A019550',
    '대성창투': 'KOREA-A027830',
    '에이티넘인베스트': 'KOREA-A021080',
}

def market_summary(code, market_name):
    session = HTMLSession()
    r = session.get('http://finance.naver.com/sise/sise_index.nhn?code={}'.format(code))
    h = r.html
    current_index_point = h.find('#now_value', first=True).text
    change = h.find('#change_value_and_rate span')[0].text

    prefix = ''
    direction_classes = h.find('#quotient', first=True).attrs['class']
    if 'up' in direction_classes:
        prefix = '▲'
    elif 'dn' in direction_classes:
        prefix = '▼'

    quantity_els = h.find('.lst_kos_info .dd span')
    quantity_personnel = quantity_els[0].text
    quantity_foreign = quantity_els[2].text
    quantity_institution = quantity_els[4].text

    result = '[{market_name}] {a} {prefix}{b} (개인 {c} / 외국인 {d} / 기관 {e})'.format(a=current_index_point, b=change, prefix=prefix, c=quantity_personnel, d=quantity_foreign, e=quantity_institution, market_name=market_name)

    return result

aliases = {
    '우기투': '우리기술투자',
    '두나무': ['우리기술투자', '카카오', 'SBI인베스트먼트', '에이티넘인베스트', '대성창투'],
    # indexes
    '코스피': lambda _: market_summary('KOSPI', '코스피'),
    '코스닥': lambda _: market_summary('KOSDAQ', '코스닥'),
}

class CodeNotfoundError(Exception):
    pass

def get_quote(quote_str):
    if quote_str in aliases:
        quote = aliases[quote_str]
    else:
        quote = quote_str
    if isinstance(quote, list):
        ret = ''
        for q in quote:
            try:
                ret += (_get_quote_kakao(q) + '\n')
            except Exception as e:
                ret += '({}: 검색실패)\n'
        return ret
    elif callable(quote):
        return quote()
    else:
        return _get_quote_kakao(quote)

info_url_format = 'http://stock.kakao.com/api/securities.json?ids={}'
code_search_url_format = 'http://stock.kakao.com/api/search/assets.json?keyword={}&limit=5'
market = '한국시장'

def get_info_url(stocks):
    if isinstance(stocks, list):
        return info_url_format.format('%2C'.join(stocks))
    if isinstance(stocks, str):
        return info_url_format.format(stocks)

def find_code(stock_name):
    code = None
    if stock_name in aliases:
        stock_name = aliases[stock_name]
    if stock_name.isdigit():
        code = 'KOREA-A{}'.format(stock_name)
    if stock_name.startswith('KOREA-A'):
        code = stock_name

    if code is None:
        if stock_name in code_cache:
            code = code_cache[stock_name]
        else:
            code_cache[stock_name] = code

        found_codes = requests.get(
            code_search_url_format.format(urllib.parse.quote_plus(stock_name))
        ).json()['assets']

        if found_codes:
            found_code = found_codes[0]
            code = found_code['assetId']
            code_cache[found_code['name']] = code
            code_cache[stock_name] = code
        else:
            raise CodeNotfoundError('코드 발견 실패: "{}" '.format(stock_name))

    return code

def _get_quote_kakao(stock_name):
    try:
        code = find_code(stock_name)
        info_url = get_info_url(code)
        info_json = requests.get(info_url.format(code)).json()['recentSecurities'][0]

        stock_name = info_json['name']
        prev_price = info_json['prevClosingPrice']
        low_price = info_json['lowPrice']
        high_price = info_json['highPrice']
        transaction_vol = info_json['globalAccTradePrice']
        price_change = info_json['changePrice']
        percentage = info_json['changePriceRate'] * 100

        if info_json['change'] == 'RISE':
            updown = '▲'
        elif info_json['change'] == 'FALL':
            updown = '▼'
        else:
            updown = '-'

        quote_price = info_json['tradePrice']
        result = ""
        result = '[{stock_name}({code})] 현재가 {quote_price:,.0f}원({updown} {price_change:,.0f}/{updown} {percentage:.2f}% / range {low_price:,.0f}원 - {high_price:,.0f}원) / 거래량 {transaction_vol:,}원 / 전일가 {prev_price:,.0f}원. '.format(stock_name=stock_name, code=code, quote_price=quote_price, low_price=low_price, high_price=high_price, transaction_vol=transaction_vol, prev_price=prev_price, updown=updown, price_change=price_change, percentage=percentage)
    except Exception as e:
        result = '[{market}] 에러! : {msg}'.format(market=market, msg=e.__repr__())

    return result


# def market_summary_naver(code, market_name):
#     session = HTMLSession()
#     r = session.get('http://finance.naver.com/sise/sise_index.nhn?code={}'.format(code))
#     h = r.html
#     current_index_point = h.find('#now_value', first=True).text
#     change = h.find('#change_value_and_rate span')[0].text

#     prefix = ''
#     direction_classes = h.find('#quotient', first=True).attrs['class']
#     if 'up' in direction_classes:
#         prefix = '▲'
#     elif 'dn' in direction_classes:
#         prefix = '▼'

#     quantity_els = h.find('.lst_kos_info .dd span')
#     quantity_personnel = quantity_els[0].text
#     quantity_foreign = quantity_els[2].text
#     quantity_institution = quantity_els[4].text

#     result = '[{market_name}] {a} {prefix}{b} (개인 {c} / 외국인 {d} / 기관 {e})'.format(a=current_index_point, b=change, prefix=prefix, c=quantity_personnel, d=quantity_foreign, e=quantity_institution, market_name=market_name)

#     return result

# def _get_quote_naver(stock_name):
#     market = '한국시장'
#     code_search_url = 'http://finance.naver.com/search/searchList.nhn?query={}'

#     def extract_text_from_nodelist(l):
#         return list(map(lambda a:a.get_text(), l))

#     try:
#         code = None
#         if stock_name in aliases:
#             stock_name = aliases[stock_name]
#         if stock_name.isdigit():
#             code = stock_name

#         if code is None:
#             if stock_name in code_cache:
#                 code = code_cache[stock_name]
#             else:
#                 code_html = requests.get(
#                     code_search_url.format(urllib.parse.quote_plus(stock_name.encode('euc-kr')))
#                 ).text
#                 code_soup = BeautifulSoup(code_html, "html.parser")
#                 lnk = code_soup.select('td.tit a')[0]
#                 found_name = lnk.get_text().replace('\n', '')
#                 if found_name == stock_name:
#                     code = lnk.get('href').split('=')[1]
#                     code_cache[stock_name] = code
#                 else:
#                     raise CodeNotfoundError('코드 발견 실패: "{}" '.format(stock_name))

#         info_html = requests.get('http://finance.naver.com/item/sise.nhn?code={}'.format(code)).text
#         info_soup = BeautifulSoup(info_html, "html.parser")

#         _is = extract_text_from_nodelist(info_soup.select('.rate_info tr td .blind'))

#         stock_name = info_soup.select('.wrap_company h2 a')[0].get_text()
#         prev_price = _is[0] # 전일가
#         low_price = _is[5] # 저가
#         high_price = _is[1] # 고가
#         transaction_vol = _is[5] # 거래대금
#         price_change, percentage = extract_text_from_nodelist(info_soup.select('.no_exday .blind'))
#         updown = info_soup.select('.no_exday .ico')[1].get_text()
#         quote_price = info_soup.select('.no_today .blind')[0].get_text() # 현재가

#         result = ""
#         result = '[{stock_name}({code})] 현재가 {quote_price}원({updown}{price_change}/{updown}{percentage}% | {low_price}원 - {high_price}원) / 거래대금 {transaction_vol}백만원 / 전일가 {prev_price}원. '.format(stock_name=stock_name, code=code, quote_price=quote_price, low_price=low_price, high_price=high_price, transaction_vol=transaction_vol, prev_price=prev_price, updown=updown, price_change=price_change, percentage=percentage)
#     except Exception as e:
#         result = '[{market}] 에러! : {msg}'.format(market=market, msg=e.__repr__())

#     return result
