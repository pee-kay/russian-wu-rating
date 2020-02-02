#!/usr/bin/env python
# -*- coding: utf-8 -*-

import game_types as gt
import datetime
import glicko
import glob
import git
import elo
import os

NEW_DIFF_I = 1000000

MILESTONES = (datetime.date(2019, 1, 1), datetime.date(2019, 4, 1),
              datetime.date(2019, 7,
                            1), datetime.date(2019, 10,
                                              1), datetime.date(2020, 1, 1))

MILESTONE_LABELS = ('2019', 'Q3 2019', 'Q2 2019', 'Q1 2019', '2018')


def format_player_info(p,
                       r,
                       rd=None,
                       i=None,
                       diff_i=None,
                       diff_r=None,
                       with_city=False):
    res = [
        '',
    ]
    if i != None:
        res.append(str(i).rjust(3))
    res.append(p.display.ljust(35))
    if with_city:
        res.append(p.city.ljust(10))
    res.append(str('   N/A' if r is None else round(r, 2)).ljust(8))
    if rd != None:
        res.append(str(round(rd, 2)).ljust(7))
    if diff_i != None:
        if diff_i == NEW_DIFF_I:
            res.append(' ---')
        elif diff_i > 0:
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
    res.append('')
    return '|'.join(res)


def format_faction_info(f, r, rd=None, i=None, diff_i=None, diff_r=None):
    res = [
        '',
    ]
    if i != None:
        res.append(str(i).rjust(3))
    res.append(f.ljust(35))
    res.append(str('   N/A' if r is None else round(r, 2)).ljust(8))
    if rd != None:
        res.append(str(round(rd, 2)).ljust(7))
    if diff_i != None:
        if diff_i == NEW_DIFF_I:
            res.append(' ---')
        elif diff_i > 0:
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
    res.append('')
    return '|'.join(res)


def export_rating(fname,
                  label,
                  tournaments,
                  players,
                  cur_date,
                  player_check=None,
                  tourney_check=None,
                  top=None,
                  with_milestones=False,
                  with_city=False,
                  min_n=6,
                  filter_date=datetime.date(2020, 1, 1),
                  max_rd_ratio=0.9,
                  system=elo,
                  with_factions=False,
                  label_factions='',
                  top_factions=None):
    try:
        r = system.Rating()
        _ = r.rdSq
        with_rd = True
    except AttributeError:
        with_rd = False

    with open(fname, 'w') as log:
        print(
            '[К основным рейтингам](https://pee-kay.github.io/russian-wu-rating)',
            file=log)

        ratings, latest_date = tournaments.rate_players(
            cur_date,
            players,
            player_check,
            tourney_check,
            sep=MILESTONES if with_milestones else (),
            min_n=min_n,
            filter_date=filter_date,
            max_rd_ratio=max_rd_ratio,
            system=system,
            with_factions=with_factions)

        print_na_info = False
        for (rating, rating_factions), m_label in zip(
                ratings[::-1],
            ('{:02}.{:02}.{}'.format(latest_date.day, latest_date.month,
                                     latest_date.year), ) + MILESTONE_LABELS):

            if with_factions:
                print('# {} {} #\n'.format(label_factions, m_label), file=log)

                cap0 = '| # |Warband                            |'
                cap1 = '|---|-----------------------------------|'
                cap0 += 'Rating  |'
                cap1 += '--------|'
                if with_rd:
                    cap0 += 'StD    |'
                    cap1 += '-------|'
                first = rating_factions is ratings[0][1]
                if not first:
                    cap0 += ' +/-|'
                    cap1 += '----|'

                print(cap0, file=log)
                print(cap1, file=log)

                prev_pos = None
                for pos, f, r, rd, diff_pos, _ in rating_factions[:len(
                        rating_factions
                ) if top_factions is None else top_factions]:
                    print(format_faction_info(
                        f, r, rd if with_rd else None,
                        pos if pos != prev_pos else '', None if first else
                        (NEW_DIFF_I if diff_pos is None else diff_pos)),
                          file=log)
                    prev_pos = pos
                    if r is None:
                        print_na_info = True

                print(file=log)

            print('# {} {} #\n'.format(label, m_label), file=log)

            cap0 = '| # |Player                             |'
            cap1 = '|---|-----------------------------------|'
            if with_city:
                cap0 += 'City      |'
                cap1 += '----------|'
            cap0 += 'Rating  |'
            cap1 += '--------|'
            if with_rd:
                cap0 += 'StD    |'
                cap1 += '-------|'
            first = rating is ratings[0][0]
            if not first:
                cap0 += ' +/-|'
                cap1 += '----|'

            print(cap0, file=log)
            print(cap1, file=log)

            prev_pos = None
            for pos, p, r, rd, diff_pos, _ in rating[:len(rating)
                                                     if top is None else top]:
                print(format_player_info(p,
                                         r,
                                         rd if with_rd else None,
                                         pos if pos != prev_pos else '',
                                         None if first else
                                         (NEW_DIFF_I if diff_pos is None else diff_pos),
                                         with_city=with_city),
                      file=log)
                prev_pos = pos
                if r is None:
                    print_na_info = True

            print(file=log)

        if with_rd:
            print('StD - среднеквадратическое отклонение рейтинга', file=log)

        if print_na_info:
            if with_rd:
                print(
                    'N/A - недостаточно определенный или устаревший рейтинг (StD < {})'
                    .format(round(system.MAX_RD * max_rd_ratio)),
                    file=log)
            else:
                print(
                    'N/A - недостаточно матчей для определения рейтинга (<{})'.
                    format(min_n),
                    file=log)

        print(
            '\n---\n\n[К основным рейтингам](https://pee-kay.github.io/russian-wu-rating)',
            file=log)


def main():
    repo = git.Repo(os.path.dirname(__file__))
    cur_date = datetime.date.fromtimestamp(repo.head.commit.committed_date)

    players_fname = 'players.csv'
    players = gt.Player.load_players(players_fname)

    tournaments = gt.Tournaments()

    for fname in glob.glob('tournaments/*.csv'):
        tournaments.load_tournament(fname, players_fname)

    for fname in glob.glob('leagues/*.csv'):
        tournaments.load_league(fname, players_fname)

    if not os.path.exists('output'):
        os.mkdir('output')

    export_rating('output/combined-top25-top10.md',
                  'Топ25 игроков',
                  tournaments,
                  players,
                  cur_date,
                  with_milestones=True,
                  with_city=True,
                  top=25,
                  with_factions=True,
                  label_factions='Топ10 банд',
                  top_factions=10)

    export_rating('output/combined-full.md',
                  'Текущий рейтинг игроков',
                  tournaments,
                  players,
                  cur_date,
                  with_city=True,
                  with_factions=True,
                  label_factions='Текущий рейтинг банд')

    export_rating('output/glass-tournaments-top25.md',
                  'Топ25 игроков России (по турнирам со стеклом)',
                  tournaments,
                  players,
                  cur_date,
                  with_milestones=True,
                  with_city=True,
                  top=25,
                  tourney_check=lambda t: t.with_glass,
                  min_n=3)

    export_rating('output/russian-top25.md',
                  'Топ25 игроков России',
                  tournaments,
                  players,
                  cur_date,
                  with_milestones=True,
                  with_city=True,
                  top=25)

    export_rating('output/russian-full.md',
                  'Текущий рейтинг игроков России',
                  tournaments,
                  players,
                  cur_date,
                  with_city=True)

    export_rating('output/moscow-top25.md',
                  'Топ25 игроков Москвы',
                  tournaments,
                  players,
                  cur_date,
                  with_milestones=True,
                  top=25,
                  player_check=lambda p: p.city == 'Msk')

    export_rating('output/moscow-full.md',
                  'Текущий рейтинг игроков Москвы',
                  tournaments,
                  players,
                  cur_date,
                  player_check=lambda p: p.city == 'Msk')

    export_rating('output/spb-top25.md',
                  'Топ25 игроков Санкт-Петербурга',
                  tournaments,
                  players,
                  cur_date,
                  with_milestones=True,
                  top=25,
                  player_check=lambda p: p.city == 'SPb')

    export_rating('output/spb-full.md',
                  'Текущий рейтинг игроков Санкт-Петербурга',
                  tournaments,
                  players,
                  cur_date,
                  player_check=lambda p: p.city == 'SPb')

    export_rating('output/shade-city-top25.md',
                  'Топ25 игроков турниров Shade City',
                  tournaments,
                  players,
                  cur_date,
                  with_milestones=True,
                  with_city=True,
                  top=25,
                  tourney_check=lambda t: t.org == 'Святослав Соколов',
                  min_n=3)

    export_rating('output/shade-city-full.md',
                  'Текущий рейтинг игроков турниров Shade City',
                  tournaments,
                  players,
                  cur_date,
                  with_city=True,
                  tourney_check=lambda t: t.org == 'Святослав Соколов',
                  min_n=3)

    export_rating('output/russian-top25-glicko.md',
                  'Топ25 игроков России (Glicko)',
                  tournaments,
                  players,
                  cur_date,
                  with_milestones=True,
                  with_city=True,
                  top=25,
                  system=glicko)

    export_rating('output/russian-full-glicko.md',
                  'Текущий рейтинг игроков России (Glicko)',
                  tournaments,
                  players,
                  cur_date,
                  with_city=True,
                  system=glicko)

    export_rating('output/moscow-top25-glicko.md',
                  'Топ25 игроков Москвы (Glicko)',
                  tournaments,
                  players,
                  cur_date,
                  with_milestones=True,
                  top=25,
                  player_check=lambda p: p.city == 'Msk',
                  system=glicko)

    export_rating('output/moscow-full-glicko.md',
                  'Текущий рейтинг игроков Москвы (Glicko)',
                  tournaments,
                  players,
                  cur_date,
                  player_check=lambda p: p.city == 'Msk',
                  system=glicko)

    export_rating('output/spb-top25-glicko.md',
                  'Топ25 игроков Санкт-Петербурга (Glicko)',
                  tournaments,
                  players,
                  cur_date,
                  with_milestones=True,
                  top=25,
                  player_check=lambda p: p.city == 'SPb',
                  system=glicko)

    export_rating('output/spb-full-glicko.md',
                  'Текущий рейтинг игроков Санкт-Петербурга (Glicko)',
                  tournaments,
                  players,
                  cur_date,
                  player_check=lambda p: p.city == 'SPb',
                  system=glicko)


if __name__ == '__main__':
    main()
