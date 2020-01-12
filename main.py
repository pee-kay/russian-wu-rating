#!/usr/bin/env python
# -*- coding: utf-8 -*-

import winrate
import elo
import glob
import datetime
from process_csv import load_players, load_tournament

class Player:
    def __init__(self, name, city='Msk', display=None):
        self.name = name
        self.city = city
        if display is None:
            self.display = name
        else:
            self.display = display

    def __str__(self):
        return self.display

    def __repr__(self):
        return 'Player({}, {}, {})'.format(repr(self.name), repr(self.city), repr(self.display))

    @staticmethod
    def create_players(*args):
        players = {}
        for arg in args:
            if isinstance(arg, tuple):
                player = Player(*arg)
            else:
                player = Player(arg)
            players[player.name] = player

        return players

class Tournament:
    def __init__(self, name, date, org, with_glass, is_grand_clash, players):
        self._name = name
        self._date = datetime.date(*date)
        self._org = org
        self._with_glass = with_glass
        self._is_grand_clash = is_grand_clash
        self._players = players
        self._matches = [[]]

    @property
    def name(self):
        return str(self._name)

    @property
    def date(self):
        return datetime.date(self._date.year, self._date.month, self._date.day)

    @property
    def org(self):
        return str(self._org)

    @property
    def with_glass(self):
        return self._with_glass

    @property
    def is_grand_clash(self):
        return self._is_grand_clash

    def end_current_tour(self):
        self._matches.append([])

    def add_match(self, p1, p2, res=1):
        if res < 0:
            self._matches[-1].append((p2, p1, False))
        elif res == 0:
            self._matches[-1].append((p1, p2, True))
        else:
            self._matches[-1].append((p1, p2, False))

    def update_ratings(self, ratings, system):
        for tour in self._matches:
            for p1, p2, drawn in tour:
                p1, p2 = self._players[p1], self._players[p2]
                if p1 not in ratings:
                    ratings[p1] = system.Rating()

                if p2 not in ratings:
                    ratings[p2] = system.Rating()

                ratings[p1], ratings[p2] = system.rate_1vs1(ratings[p1], ratings[p2], drawn)

class Tournaments(list):
    def create(self, *args, **kwargs):
        tourney = Tournament(*args, **kwargs)
        self.append(tourney)
        return tourney

    def rate_players(self, players, player_check = None, tourney_check = None, system = elo):
        ratings = {}

        for tourney in sorted(self, key = lambda t: t.date):
            if tourney_check is not None and not tourney_check(tourney):
                continue

            tourney.update_ratings(ratings, system)

        result = []
        for p, r in sorted(ratings.items(), key=lambda pr: pr[1].mu, reverse=True):
            player = players[p]
            if player_check is not None and not player_check(player):
                continue

            if system is winrate and r.n < 5:
                continue

            result.append((player, r.mu))

        return result

def main():
    players_fname = 'players.csv'
    players = Player.create_players(*load_players(players_fname).values())

    tournaments = Tournaments()
    for fname in glob.glob('tournaments/*.csv'):
        load_tournament(fname, tournaments, players_fname)

    # TODO: попробовать добавить командник 'Shadeglass Crusade': https://docs.google.com/spreadsheets/d/1rdY1WNSRE1moKqVWZMxHGJlBaxPiC02wa-Ko5BeRo5M/edit#gid=0

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