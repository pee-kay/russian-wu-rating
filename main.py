#!/usr/bin/env python
# -*- coding: utf-8 -*-

import game_types as gt
import datetime
import glob
import git
import os


def get_player_line(p, r, i=None, diff_i=None, diff_r=None, with_city=False):
    res = []
    if i != None:
        res.append(str(i).rjust(3))
    res.append(p.display.ljust(25)[:25])
    if with_city:
        res.append(p.city.ljust(10)[:10])
    res.append(str(round(r, 2)).ljust(8)[:8])
    if diff_i != None:
        if diff_i > 0:
            res.append(('+' + str(diff_i)).rjust(4))
        elif diff_i == 0:
            res.append('    ')
        else:
            res.append(str(diff_i).rjust(4))
    if diff_r != None:
        if diff_r >= 0:
            res.append(('+' + str(diff_i)).rjust(8))
        else:
            res.append(str(diff_i).rjust(8))
    return '|'.join(res)


def main():
    repo = git.Repo(os.path.dirname(__file__))
    cur_date = datetime.date.fromtimestamp(repo.head.commit.committed_date)
    cur_date_str = '{:02}.{:02}.{}'.format(
        cur_date.day, cur_date.month, cur_date.year)

    players_fname = 'players.csv'
    players = gt.Player.load_players(players_fname)

    tournaments = gt.Tournaments()

    for fname in glob.glob('tournaments/*.csv'):
        tournaments.load_tournament(fname, players_fname)

    for fname in glob.glob('leagues/*.csv'):
        tournaments.load_league(fname, players_fname)

    if not os.path.exists('output'):
        os.mkdir('output')

    with open('output/glass_tournaments_top25.md', 'w') as log:
        ratings = tournaments.rate_players(cur_date, players, tourney_check=lambda t: t.with_glass and t.date <= cur_date, sep=(
            datetime.date(2019, 1, 1), datetime.date(2019, 4, 1), datetime.date(2019, 7, 1), datetime.date(2019, 10, 1), datetime.date(2020, 1, 1)))
        for rating, label in zip(ratings[::-1],
                                 ['Топ25 игроков России {} (по турнирам со стеклом)'.format(cur_date_str),
                                  'Топ25 игроков России 2019 (по турнирам со стеклом)',
                                  'Топ25 игроков России Q3 2019 (по турнирам со стеклом)',
                                  'Топ25 игроков России Q2 2019 (по турнирам со стеклом)',
                                  'Топ25 игроков России Q1 2019 (по турнирам со стеклом)',
                                  'Топ25 игроков России 2018 (по турнирам со стеклом)']):
            print(label, file=log)
            print('=' * len(label), file=log)
            if rating is ratings[0]:
                print(' # |Player                   |City      |Rating  ', file=log)
                print('---|-------------------------|----------|--------', file=log)
            else:
                print(' # |Player                   |City      |Rating  | +/-', file=log)
                print('---|-------------------------|----------|--------|----', file=log)
            for i, (p, r, diff_i, _) in enumerate(rating[:25]):
                print(get_player_line(
                    p, r, i + 1, None if rating is ratings[0] else (0 if diff_i is None else diff_i), with_city=True), file=log)
            print(file=log)

    with open('output/russian_top25.md', 'w') as log:
        ratings = tournaments.rate_players(cur_date, players, tourney_check=lambda t: t.date <= cur_date, sep=(
            datetime.date(2019, 1, 1), datetime.date(2019, 4, 1), datetime.date(2019, 7, 1), datetime.date(2019, 10, 1), datetime.date(2020, 1, 1)))
        for rating, label in zip(ratings[::-1],
                                 ['Топ25 игроков России {}'.format(cur_date_str),
                                  'Топ25 игроков России 2019',
                                  'Топ25 игроков России Q3 2019',
                                  'Топ25 игроков России Q2 2019',
                                  'Топ25 игроков России Q1 2019',
                                  'Топ25 игроков России 2018']):
            print(label, file=log)
            print('=' * len(label), file=log)
            if rating is ratings[0]:
                print(' # |Player                   |City      |Rating  ', file=log)
                print('---|-------------------------|----------|--------', file=log)
            else:
                print(' # |Player                   |City      |Rating  | +/-', file=log)
                print('---|-------------------------|----------|--------|----', file=log)
            for i, (p, r, diff_i, _) in enumerate(rating[:25]):
                print(get_player_line(
                    p, r, i + 1, None if rating is ratings[0] else (0 if diff_i is None else diff_i), with_city=True), file=log)
            print(file=log)

    with open('output/russian_full.md', 'w') as log:
        ratings = tournaments.rate_players(
            cur_date, players, tourney_check=lambda t: t.date <= cur_date)
        for rating, label in zip(ratings[::-1],
                                 ['Полный рейтинг игроков России {}'.format(cur_date_str)]):
            print(label, file=log)
            print('=' * len(label), file=log)
            if rating is ratings[0]:
                print(' # |Player                   |City      |Rating  ', file=log)
                print('---|-------------------------|----------|--------', file=log)
            else:
                print(' # |Player                   |City      |Rating  | +/-', file=log)
                print('---|-------------------------|----------|--------|----', file=log)
            for i, (p, r, diff_i, _) in enumerate(rating):
                print(get_player_line(
                    p, r, i + 1, None if rating is ratings[0] else (0 if diff_i is None else diff_i), with_city=True), file=log)
            print(file=log)

    with open('output/moscow_top25.md', 'w') as log:
        ratings = tournaments.rate_players(cur_date, players, lambda p: p.city == 'Msk', lambda t: t.date <= cur_date, sep=(
            datetime.date(2019, 1, 1), datetime.date(2019, 4, 1), datetime.date(2019, 7, 1), datetime.date(2019, 10, 1), datetime.date(2020, 1, 1)))
        for rating, label in zip(ratings[::-1],
                                 ['Топ25 игроков Москвы {}'.format(cur_date_str),
                                  'Топ25 игроков Москвы 2019',
                                  'Топ25 игроков Москвы Q3 2019',
                                  'Топ25 игроков Москвы Q2 2019',
                                  'Топ25 игроков Москвы Q1 2019',
                                  'Топ25 игроков Москвы 2018']):
            print(label, file=log)
            print('=' * len(label), file=log)
            if rating is ratings[0]:
                print(' # |Player                   |Rating  ', file=log)
                print('---|-------------------------|--------', file=log)
            else:
                print(' # |Player                   |Rating  | +/-', file=log)
                print('---|-------------------------|--------|----', file=log)
            for i, (p, r, diff_i, _) in enumerate(rating[:25]):
                print(get_player_line(
                    p, r, i + 1, None if rating is ratings[0] else (0 if diff_i is None else diff_i)), file=log)
            print(file=log)

    with open('output/moscow_full.md', 'w') as log:
        ratings = tournaments.rate_players(
            cur_date, players, lambda p: p.city == 'Msk', lambda t: t.date <= cur_date)
        for rating, label in zip(ratings[::-1],
                                 ['Полный рейтинг игроков Москвы {}'.format(cur_date_str)]):
            print(label, file=log)
            print('=' * len(label), file=log)
            if rating is ratings[0]:
                print(' # |Player                   |Rating  ', file=log)
                print('---|-------------------------|--------', file=log)
            else:
                print(' # |Player                   |Rating  | +/-', file=log)
                print('---|-------------------------|--------|----', file=log)
            for i, (p, r, diff_i, _) in enumerate(rating):
                print(get_player_line(
                    p, r, i + 1, None if rating is ratings[0] else (0 if diff_i is None else diff_i)), file=log)
            print(file=log)

    with open('output/spb_top25.md', 'w') as log:
        ratings = tournaments.rate_players(cur_date, players, lambda p: p.city == 'SPb', lambda t: t.date <= cur_date, sep=(
            datetime.date(2019, 1, 1), datetime.date(2019, 4, 1), datetime.date(2019, 7, 1), datetime.date(2019, 10, 1), datetime.date(2020, 1, 1)))
        for rating, label in zip(ratings[::-1],
                                 ['Топ25 игроков Санкт-Петербурга {}'.format(cur_date_str),
                                  'Топ25 игроков Санкт-Петербурга 2019',
                                  'Топ25 игроков Санкт-Петербурга Q3 2019',
                                  'Топ25 игроков Санкт-Петербурга Q2 2019',
                                  'Топ25 игроков Санкт-Петербурга Q1 2019',
                                  'Топ25 игроков Санкт-Петербурга 2018']):
            print(label, file=log)
            print('=' * len(label), file=log)
            if rating is ratings[0]:
                print(' # |Player                   |Rating  ', file=log)
                print('---|-------------------------|--------', file=log)
            else:
                print(' # |Player                   |Rating  | +/-', file=log)
                print('---|-------------------------|--------|----', file=log)
            for i, (p, r, diff_i, _) in enumerate(rating[:25]):
                print(get_player_line(
                    p, r, i + 1, None if rating is ratings[0] else (0 if diff_i is None else diff_i)), file=log)
            print(file=log)

    with open('output/spb_full.md', 'w') as log:
        ratings = tournaments.rate_players(
            cur_date, players, lambda p: p.city == 'SPb', lambda t: t.date <= cur_date)
        for rating, label in zip(ratings[::-1],
                                 ['Полный рейтинг игроков Санкт-Петербурга {}'.format(cur_date_str)]):
            print(label, file=log)
            print('=' * len(label), file=log)
            if rating is ratings[0]:
                print(' # |Player                   |Rating  ', file=log)
                print('---|-------------------------|--------', file=log)
            else:
                print(' # |Player                   |Rating  | +/-', file=log)
                print('---|-------------------------|--------|----', file=log)
            for i, (p, r, diff_i, _) in enumerate(rating):
                print(get_player_line(
                    p, r, i + 1, None if rating is ratings[0] else (0 if diff_i is None else diff_i)), file=log)
            print(file=log)

    with open('output/shade_city_top25.md', 'w') as log:
        ratings = tournaments.rate_players(cur_date, players, tourney_check=lambda t: t.org == 'Святослав Соколов' and t.date <= cur_date, sep=(
            datetime.date(2019, 1, 1), datetime.date(2019, 4, 1), datetime.date(2019, 7, 1), datetime.date(2019, 10, 1), datetime.date(2020, 1, 1)))
        for rating, label in zip(ratings[::-1],
                                 ['Топ25 игроков турниров Shade City {}'.format(cur_date_str),
                                  'Топ25 игроков турниров Shade City 2019',
                                  'Топ25 игроков турниров Shade City Q3 2019',
                                  'Топ25 игроков турниров Shade City Q2 2019',
                                  'Топ25 игроков турниров Shade City Q1 2019',
                                  'Топ25 игроков турниров Shade City 2018']):
            print(label, file=log)
            print('=' * len(label), file=log)
            if rating is ratings[0]:
                print(' # |Player                   |City      |Rating  ', file=log)
                print('---|-------------------------|----------|--------', file=log)
            else:
                print(' # |Player                   |City      |Rating  | +/-', file=log)
                print('---|-------------------------|----------|--------|----', file=log)
            for i, (p, r, diff_i, _) in enumerate(rating[:25]):
                print(get_player_line(
                    p, r, i + 1, None if rating is ratings[0] else (0 if diff_i is None else diff_i), with_city=True), file=log)
            print(file=log)

    with open('output/shade_city_full.md', 'w') as log:
        ratings = tournaments.rate_players(
            cur_date, players, tourney_check=lambda t: t.org == 'Святослав Соколов' and t.date <= cur_date)
        for rating, label in zip(ratings[::-1],
                                 ['Полный рейтинг игроков турниров Shade City {}'.format(cur_date_str)]):
            print(label, file=log)
            print('=' * len(label), file=log)
            if rating is ratings[0]:
                print(' # |Player                   |City      |Rating  ', file=log)
                print('---|-------------------------|----------|--------', file=log)
            else:
                print(' # |Player                   |City      |Rating  | +/-', file=log)
                print('---|-------------------------|----------|--------|----', file=log)
            for i, (p, r, diff_i, _) in enumerate(rating):
                print(get_player_line(
                    p, r, i + 1, None if rating is ratings[0] else (0 if diff_i is None else diff_i), with_city=True), file=log)
            print(file=log)


if __name__ == '__main__':
    main()
