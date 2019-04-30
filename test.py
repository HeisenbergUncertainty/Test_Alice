from flask import Flask, request
import logging
import json
import os
import requests
import sys

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s %(levelname)s %(name)s %(message)s')

sessionStorage = {}
con = []
player_deck = []
alise_deck = []
move = 0

@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {'end_session': False}}
    handle_dialog(response, request.json)
    logging.info('Request: %r', response)
    return json.dumps(response)


def handle_dialog(res, req):
    if req['session']['new']:
        deck_id = new_deck()
#         sessionStorage[user_id] = {'suggests': [{'title': "Да", 'hide': True}, {'title': "Нет", 'hide': True}]}
        alise_deck = translate(give_cards(deck_id, 6)['cards'])
        player_deck = translate(give_cards(deck_id, 6)['cards'])
        res['response']['text'] = 'Твоя колода'
        res['response']['text'] = player_deck
        res['response']['buttons'] = sessionStorage[user_id]['suggests']

        return

    elif move == 0:
        if not (req['request']['original_utterance'] in '123456'):
            res['response']['text'] = 'Не понимаю'
            return

        con = player_deck.pop(req['request']['original_utterance'] - 1)
        res['response']['text'] = 'Ты кинул(а)'
        res['response']['text'] = con
        card = find_card(alise_deck, con['price'])

        if not card:
            alise_deck.append(con)
            res['response']['text'] = 'Взяла'
            return

        res['response']['text'] = alise_deck.pop(card)

        alise_deck.append(translate(give_cards(deck_id, 1)['cards']))
        player_deck.append(translate(give_cards(deck_id, 1)['cards']))
        res['response']['text'] = 'Твоя новая карта'
        res['response']['text'] = player_deck[-1]

        res['response']['text'] = 'Это тебе'
        con = alise_deck.pop(card)
        res['response']['text'] = con
        move = 1

    elif move == 1:
        if not (req['request']['original_utterance'] in '123456' or
                req['request']['original_utterance'] in 'Взять карту'):
            res['response']['text'] = 'Не понимаю'
            return

        if req['request']['original_utterance'] == 'Взять карту':
            player_deck.append(con)
            res['response']['text'] = 'Твоя колода'
            res['response']['text'] = player_deck
            return

        player_card = player_deck.pop(req['request']['original_utterance'])
        move = 0

    return


def new_deck():
    response = requests.get(
        'https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1')
    deck_id1 = response.json()["deck_id"]
    return deck_id1


def give_cards(id, n):
    response = requests.get(
        'https://deckofcardsapi.com/api/deck/{}/shuffle/'.format(id)).json()

    if n > response["remaining"]:
        n = response["remaining"]

    response = requests.get(
        'https://deckofcardsapi.com/api/deck/{}/draw/?count={}'.format(id,
                                                                       n)).json()
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

        ans.append({'value': x['value'], 'suit': x['suit'], 'price': price})

    return ans


def find_card(data, n):
    for i in len(data):
        if data[i]['price'] > n:
            return i
    return False


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
