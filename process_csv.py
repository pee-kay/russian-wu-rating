import csv
import os

def load_players(fname):
    players = {}

    with open(fname, 'r') as csvf:
        rdr = csv.reader(csvf)
        for l in rdr:
            if l[0] in players:
                raise RuntimeError('Player duplicate {}'.format(l))

            players[l[0]] = (l[0], l[1], l[0] if l[2] == '' else l[2])

    return players

def load_tournament(fname, tournaments = None, players_fname = 'players.csv'):
    tour_n = 1
    players = []
    tables = set()
    with open(fname, 'r') as csvf:
        rdr = csv.reader(csvf)
        for i, l in enumerate(rdr):
            if i == 0:
                tour_n = l.count(l[3])
                if tour_n > 1 and l[3] != l[7]:
                    raise RuntimeError('Wrong csv, missing table column')
                continue

            name = l[1].strip()
            tours = [(l[3 + j * 4], l[4 + j * 4]) for j in range(tour_n)]
            tables = tables.union(set([t[0] for t in tours]))
            players.append((i, name, tours))

    tourney_players = {}
    missing_players = []
    existing_players = load_players(players_fname)
    for i, name, _ in players:
        if name not in existing_players and name != 'Proxy':
            missing_players.append(name)

        tourney_players[i] = name

    if missing_players:
        raise RuntimeError('Missing players: {}'.format(missing_players))

    if tournaments is not None:
        gl = {}
        exec('params = ({})'.format(os.path.splitext(os.path.basename(fname))[0]), gl)
        name, date, org, with_glass = gl['params']

        tourney = tournaments.create(name, date, org, with_glass, tourney_players)

        for tour in range(tour_n):
            for t in sorted(tables):
                table = []
                for i, name, tours in players:
                    if name != 'Proxy' and tours[tour][0] == t:
                        table.append((i, tours[tour][1]))

                if len(table) < 2:
                    continue

                if len(table) > 2:
                    raise RuntimeError('Too many players on the same table')

                i1 = table[0][0]
                i2 = table[1][0]
                res = 1 if table[0][1] > table[1][1] else (-1 if table[0][1] < table[1][1] else 0)
                tourney.add_match(i1, i2, res)

if __name__ == '__main__':
    import sys
    load_tournament(sys.argv[1])