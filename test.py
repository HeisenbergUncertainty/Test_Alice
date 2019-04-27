from flask import Flask, request
import logging
import requests
import json

app = Flask(__name__)


logging.basicConfig(level=logging.INFO)

sessionStorage = {}

@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info('Request: %r', response)
    return json.dumps(response)


def handle_dialog(res, req):
    con = []
    player_deck = []
    alise_deck = []
    deck_id = 0
    move = 0
    res['response']['text'] = ''

    if req['session']['new']:
        deck_id = new_deck()
        alise_deck = translate(give_cards(deck_id, 6)['cards'])
        player_deck = translate(give_cards(deck_id, 6)['cards'])
        res['response']['text'] += '\nТвоя колода'
        res['response']['text'] += '\n'
        res['response']['text'] += player_deck
        return

    if move == 0:
        if not (req['request']['original_utterance'] in '123456'):
            res['response']['text'] += '\nНе понимаю'
            return

        con = player_deck.pop(req['request']['original_utterance'] - 1)
        res['response']['text'] += '\nТы кинул(а)\n'
        res['response']['text'] += con
        card = find_card(alise_deck, con['price'])

        if not card:
            alise_deck.append(con)
            res['response']['text'] += '\nВзяла'
            return

        res['response']['text'] += '\n'
        res['response']['text'] += alise_deck.pop(card)

        alise_deck.append(translate(give_cards(deck_id, 1)['cards']))
        player_deck.append(translate(give_cards(deck_id, 1)['cards']))
        res['response']['text'] += '\nТвоя новая карта\n'
        res['response']['text'] += player_deck[-1]

        res['response']['text'] += '\nЭто тебе\n'
        con = alise_deck.pop(card)
        res['response']['text'] += con
        move = 1

    elif move == 1:
        if not (req['request']['original_utterance'] in '123456' or
                        req['request']['original_utterance'] in 'Взять карту'):
            res['response']['text'] += '\nНе понимаю'
            return

        if req['request']['original_utterance'] == 'Взять карту':
            player_deck.append(con)
            res['response']['text'] += '\nТвоя колода\n'
            res['response']['text'] += player_deck
            return

        player_card = player_deck.pop(req['request']['original_utterance'])
        move = 0

    return



def new_deck():
    response = requests.get('https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1')
    deck_id = response.json()["deck_id"]
    return deck_id

def give_cards(id, n):
    response = requests.get('https://deckofcardsapi.com/api/deck/{}/shuffle/'.format(id)).json()

    if n > response["remaining"]:
        n = response["remaining"]

    response = requests.get('https://deckofcardsapi.com/api/deck/{}/draw/?count={}'.format(id, n)).json()
    return response

def translate(data):
    ans = []
    for x in data:
        price = x['value']
        if price.isdigit():
            price = int(x['suit'])
        else:
            if price == 'ACE':
                price = 14
            elif price == 'JACK':
                price = 11
            elif price == 'QUEEN':
                price = 12
            elif price == 'KING':
                price = 13

        ans.append({'value':x['value'], 'suit': x['suit'], 'price': price})

    return ans

def find_card(data, n):
    for i in len(data):
        if data[i]['price'] > n:
            return i
    return False

if __name__ == '__main__':
    app.run()
