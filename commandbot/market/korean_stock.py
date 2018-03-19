# -*- coding: utf-8 -*-
import requests
import urllib.parse
from requests_html import HTMLSession
from bs4 import BeautifulSoup


code_cache = {
    '우리기술투자': '041190',
    '카카오': '035720',
    'SBI인베스트먼트': '019550',
    '대성창투': '027830',
    '에이티넘인베스트': '021080',
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

def market_summary_kospi():
    return market_summary('KOSPI', '코스피')

def market_summary_kosdaq():
    return market_summary('KOSDAQ', '코스닥')

aliases = {
    '우기투': '우리기술투자',
    '두나무': ['우리기술투자', '카카오', 'SBI인베스트먼트', '에이티넘인베스트', '대성창투'],
    # indexes
    '코스피': market_summary_kospi,
    '코스닥': market_summary_kosdaq,
}


class CodeNotfoundError(Exception):
    pass

code_search_url = 'http://finance.naver.com/search/searchList.nhn?query={}'

def extract_text_from_nodelist(l):
    return list(map(lambda a:a.get_text(), l))

def get_quote(quote_str):
    if quote_str in aliases:
        quote = aliases[quote_str]
    else:
        quote = quote_str
    if isinstance(quote, list):
        ret = ''
        for q in quote:
            try:
                ret += (_get_quote(q) + '\n')
            except Exception as e:
                ret += '({}: 검색실패)\n'
        return ret
    elif callable(quote):
        return quote()
    else:
        return _get_quote(quote)

def _get_quote(stock_name):
    market = '한국시장'

    try:
        code = None
        if stock_name in aliases:
            stock_name = aliases[stock_name]
        if stock_name.isdigit():
            code = stock_name

        if code is None:
            if stock_name in code_cache:
                code = code_cache[stock_name]
            else:
                code_html = requests.get(
                    code_search_url.format(urllib.parse.quote_plus(stock_name.encode('euc-kr')))
                ).text
                code_soup = BeautifulSoup(code_html, "html.parser")
                lnk = code_soup.select('td.tit a')[0]
                found_name = lnk.get_text().replace('\n', '')
                if found_name == stock_name:
                    code = lnk.get('href').split('=')[1]
                    code_cache[stock_name] = code
                else:
                    raise CodeNotfoundError('코드 발견 실패: "{}" '.format(stock_name))

        info_html = requests.get('http://finance.naver.com/item/sise.nhn?code={}'.format(code)).text
        info_soup = BeautifulSoup(info_html, "html.parser")

        _is = extract_text_from_nodelist(info_soup.select('.rate_info tr td .blind'))

        stock_name = info_soup.select('.wrap_company h2 a')[0].get_text()
        prev_price = _is[0] # 전일가
        low_price = _is[5] # 저가
        high_price = _is[1] # 고가
        transaction_vol = _is[5] # 거래대금
        price_change, percentage = extract_text_from_nodelist(info_soup.select('.no_exday .blind'))
        updown = info_soup.select('.no_exday .ico')[1].get_text()
        quote_price = info_soup.select('.no_today .blind')[0].get_text() # 현재가

        result = ""
        result = '[{stock_name}({code})] 현재가 {quote_price}원({updown}{price_change}/{updown}{percentage}% | {low_price}원 - {high_price}원) / 거래대금 {transaction_vol}백만원 / 전일가 {prev_price}원. '.format(stock_name=stock_name, code=code, quote_price=quote_price, low_price=low_price, high_price=high_price, transaction_vol=transaction_vol, prev_price=prev_price, updown=updown, price_change=price_change, percentage=percentage)
    except Exception as e:
        result = '[{market}] 에러! : {msg}'.format(market=market, msg=e.__repr__())

    return result
