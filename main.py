#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
from game_types import *

def main():
    players_fname = 'players.csv'
    players = Player.load_players(players_fname)

    tournaments = Tournaments()

    for fname in glob.glob('tournaments/*.csv'):
        tournaments.load_tournament(fname, players_fname)

    for fname in glob.glob('leagues/*.csv'):
        tournaments.load_league(fname, players_fname)

    print('Топ25 игроков России (по турнирам со стеклом)')
    print('=============================================')
    for i, (p, r) in enumerate(tournaments.rate_players(players, tourney_check = lambda t: t.with_glass)[:25]):
        print(str(i + 1).rjust(3), p.display.ljust(25), p.city.ljust(10), round(r, 2))
    print()

    print('Топ15 игроков Москвы (по турнирам со стеклом)')
    print('=============================================')
    for i, (p, r) in enumerate(tournaments.rate_players(players, lambda p: p.city == 'Msk', lambda t: t.with_glass)[:15]):
        print(str(i + 1).rjust(3), p.display.ljust(25), round(r, 2))
    print()

    print('Топ15 игроков Москвы (по всем добавленным турнирам и лигам)')
    print('===========================================================')
    for i, (p, r) in enumerate(tournaments.rate_players(players, lambda p: p.city == 'Msk')[:15]):
        print(str(i + 1).rjust(3), p.display.ljust(25), round(r, 2))
    print()

    print('Топ15 игроков Москвы (по турнирам @vapour_crow)')
    print('===============================================')
    for i, (p, r) in enumerate(tournaments.rate_players(players, lambda p: p.city == 'Msk', lambda t: t.org == 'Святослав Соколов')[:15]):
        print(str(i + 1).rjust(3), p.display.ljust(25), round(r, 2))
    print()

    print('Рейтинг игроков Москвы (по всем добавленным турнирам и лигам)')
    print('=============================================================')
    for i, (p, r) in enumerate(tournaments.rate_players(players, lambda p: p.city == 'Msk')):
        print(str(i + 1).rjust(3), p.display.ljust(25), round(r, 2))
    print()

    print('Рейтинг игроков Санкт-Петербурга')
    print('================================')
    for i, (p, r) in enumerate(tournaments.rate_players(players, lambda p: p.city == 'SPb')):
        print(str(i + 1).rjust(3), p.display.ljust(25), round(r, 2))
    print()

if __name__ == '__main__':
    main()