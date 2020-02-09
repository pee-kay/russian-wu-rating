import datetime
import winrate
import elo
import csv
import os

RANKS = {'LG': 0, 'LT': 1, 'GT': 2, 'TC': 2, 'GC': 3, 'GM': 4}


class Player:
    def __init__(self, name, city='Msk', display=None, hidden=False):
        self.name = name
        self.city = city
        self.hidden = hidden
        if display is None:
            self.display = name
        else:
            self.display = display

    def __str__(self):
        return self.display

    def __repr__(self):
        return 'Player({}, {}, {})'.format(repr(self.name), repr(self.city),
                                           repr(self.display))

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

    @staticmethod
    def load_players(fname):
        players = []
        player_names = set()

        with open(fname, 'r') as csvf:
            rdr = csv.reader(csvf)
            for l in rdr:
                if l[0] in player_names:
                    raise RuntimeError('Player duplicate {}'.format(l))

                hidden = False
                if l[2].startswith('NONE'):
                    l[2] = l[2][4:]
                    hidden = True

                players.append((l[0], l[1], l[0] if l[2] == '' else l[2], hidden))
                player_names = player_names.union(set(l[0]))

        return Player.create_players(*players)


class Faction:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'Faction({})'.format(repr(self.name))

    @staticmethod
    def load_factions(fname):
        factions = {}

        with open(fname, 'r') as csvf:
            rdr = csv.reader(csvf)
            for l in rdr:
                factions[l[0]] = Faction(l[0])
                factions[l[0].lower()] = factions[l[0]]
                factions[l[0].replace("'", "’").lower()] = factions[l[0]]
                if l[1]:
                    for s in l[1].split('|'):
                        factions[s.lower()] = factions[l[0]]

        return factions


class Tournament:
    def __init__(self, name, date, org, city, tt, players, factions={}):
        self._name = name
        self._date = datetime.date(*date)
        self._org = org
        self._city = city
        self._rank = RANKS[tt]
        self._players = players
        self._factions = factions
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
    def city(self):
        return str(self._city)

    @property
    def with_glass(self):
        return self._rank >= 2

    @property
    def is_grand_clash(self):
        return self._rank >= 3

    @property
    def rank(self):
        return self._rank

    def end_current_tour(self):
        self._matches.append([])

    def add_match(self, p1, p2, res=1, f1=None, f2=None):
        if f1 is None and self._factions:
            f1 = self._factions[p1]
        if f2 is None and self._factions:
            f2 = self._factions[p2]
        if res < 0:
            self._matches[-1].append((p2, p1, False, f2, f1))
        elif res == 0:
            self._matches[-1].append((p1, p2, True, f1, f2))
        else:
            self._matches[-1].append((p1, p2, False, f1, f2))

    def check_players(self, players, player_check):
        for p in self._players:
            if self._players[p] == 'Proxy':
                continue

            if player_check(players[self._players[p]]):
                return True

        return False

    def update_ratings(self, ratings, system, faction_ratings=None):
        for tour in self._matches:
            for p1, p2, drawn, f1, f2 in tour:
                p1, p2 = self._players[p1], self._players[p2]
                if p1 not in ratings:
                    ratings[p1] = system.Rating()

                if p2 not in ratings:
                    ratings[p2] = system.Rating()

                if faction_ratings != None and f1 != None and f2 != None and f1 != f2:
                    if f1 not in faction_ratings:
                        faction_ratings[f1] = system.Rating()

                    if f2 not in faction_ratings:
                        faction_ratings[f2] = system.Rating()

                    ratings[p1], ratings[p2], faction_ratings[
                        f1], faction_ratings[f2] = system.rate_2vs2(
                            ratings[p1],
                            ratings[p2],
                            faction_ratings[f1],
                            faction_ratings[f2],
                            drawn,
                            date=self.date)
                else:
                    ratings[p1], ratings[p2] = system.rate_1vs1(ratings[p1],
                                                                ratings[p2],
                                                                drawn,
                                                                date=self.date)

    def update_prob(self, ratings, prob, diff_step):
        for tour in self._matches:
            for p1, p2, drawn, _, _ in tour:
                p1, p2 = self._players[p1], self._players[p2]
                r1, r2 = ratings[p1], ratings[p2]

                diff = abs(r1.mu - r2.mu)
                while diff >= prob[0][-1]:
                    prob[0].append(prob[0][-1] + diff_step)
                    prob[1].append(0)
                    prob[2].append(0.0)

                diff_i = 0
                for i, bnd in enumerate(prob[0]):
                    if bnd > diff:
                        diff_i = i
                        break

                upd = 0.5 if drawn else (1 if r1.mu >= r2.mu else 0)

                prob[1][diff_i] += 1
                prob[2][diff_i] += upd


class League(Tournament):
    def __init__(self, name, start_date, org, city, players):
        super().__init__(name, start_date, org, city, 'LG', players)
        self._start_date = self._date
        self._match_dates = [[]]

    def end_current_tour(self):
        super().end_current_tour()
        self._match_dates.append([])

    def add_match(self, p1, p2, res=1, date=None, f1=None, f2=None):
        super().add_match(p1, p2, res, f1, f2)

        date = self._date if date is None else date
        self._match_dates[-1].append(date)

        if date < self._start_date:
            raise RuntimeError(
                'Match couldn\'t happen before start of the league')

        if date > self._date:
            self._date = date


class Tournaments(list):
    def create(self, *args, **kwargs):
        tourney = Tournament(*args, **kwargs)
        self.append(tourney)
        return tourney

    def create_league(self, *args, **kwargs):
        tourney = League(*args, **kwargs)
        self.append(tourney)
        return tourney

    def rate_players(self,
                     cur_date,
                     players,
                     player_check=None,
                     tourney_check=None,
                     system=elo,
                     sep=(),
                     min_n=5,
                     filter_date=None,
                     max_rd_ratio=0.9,
                     with_factions=False):
        try:
            r = system.Rating()
            _ = r.rdSq
            with_rd = True
        except AttributeError:
            with_rd = False

        class State:
            def __init__(self, with_factions):
                self.ratings = {}
                self.faction_ratings = {} if with_factions else None
                self.result = []
                self.prev_ids = {}
                self.prev_faction_ids = {}

            def separate(self, date):
                self.result.append(([], []))

                def check_rating(r):
                    return r.getRdSq(
                        date
                    ) < system.MAX_RD_SQ * max_rd_ratio * max_rd_ratio if with_rd else r.n >= min_n or filter_date is None or date <= filter_date

                ids = {}
                if self.faction_ratings:
                    for faction, r in sorted(
                            self.faction_ratings.items(),
                            key=lambda fr:
                        (-fr[1].mu if check_rating(fr[1]) else 0, fr[0])):

                        rating = r.mu if check_rating(r) else None

                        if self.result[-1][1]:
                            new = rating != self.result[-1][1][-1][2]
                            position = len(
                                self.result[-1]
                                [1]) + 1 if new else self.result[-1][1][-1][0]
                        else:
                            new = True
                            position = 1

                        diff_p = None
                        diff_r = None
                        if faction in self.prev_faction_ids:
                            prev_i = self.prev_faction_ids[faction]
                            diff_p = self.result[-2][1][prev_i][0] - position
                            if rating != None and self.result[-2][1][prev_i][
                                    2] != None:
                                diff_r = rating - self.result[-2][1][prev_i][2]

                        ids[faction] = len(self.result[-1][1])
                        self.result[-1][1].append(
                            (position, faction, rating,
                             r.getRdSq(date)**0.5 if with_rd else 0, diff_p,
                             diff_r))

                self.prev_faction_ids = ids

                ids = {}
                for p, r in sorted(
                        self.ratings.items(),
                        key=lambda pr:
                    (-pr[1].mu
                     if check_rating(pr[1]) else 0, players[pr[0]].display)):
                    player = players[p]
                    if player_check is not None and not player_check(player):
                        continue

                    if player.hidden:
                        continue

                    rating = r.mu if check_rating(r) else None

                    if self.result[-1][0]:
                        new = rating != self.result[-1][0][-1][2]
                        position = len(
                            self.result[-1]
                            [0]) + 1 if new else self.result[-1][0][-1][0]
                    else:
                        new = True
                        position = 1

                    diff_p = None
                    diff_r = None
                    if player.name in self.prev_ids:
                        prev_i = self.prev_ids[player.name]
                        diff_p = self.result[-2][0][prev_i][0] - position
                        if rating != None and self.result[-2][0][prev_i][
                                2] != None:
                            diff_r = rating - self.result[-2][0][prev_i][2]

                    ids[player.name] = len(self.result[-1][0])
                    self.result[-1][0].append(
                        (position, player, rating,
                         r.getRdSq(date)**0.5 if with_rd else 0, diff_p,
                         diff_r))

                self.prev_ids = ids

        state = State(with_factions)
        latest_date = None
        for tourney in sorted(self, key=lambda t: t.date):
            if tourney_check is not None and not tourney_check(tourney):
                continue

            while sep and tourney.date >= sep[0]:
                state.separate(sep[0])
                latest_date = sep[0]
                sep = sep[1:]

            tourney.update_ratings(state.ratings, system,
                                   state.faction_ratings)

            if player_check is None or tourney.check_players(
                    players, player_check):
                latest_date = tourney.date

        while sep:
            state.separate(sep[0])
            latest_date = sep[0]
            sep = sep[1:]

        state.separate(cur_date if latest_date is None else latest_date)

        return state.result, cur_date if latest_date is None else latest_date

    def rate_prob(self, players, system=elo, diff_step=1):
        ratings = {}

        for tourney in sorted(self, key=lambda t: t.date):
            tourney.update_ratings(ratings, system)

        prob = [[diff_step], [0], [0.0]]
        for tourney in sorted(self, key=lambda t: t.date):
            tourney.update_prob(ratings, prob, diff_step)

        return prob

    def load_tournament(self,
                        fname,
                        players_fname='players.csv',
                        factions_fname='factions.csv'):
        tb_cols = []
        vp_cols = []
        nm_cols = []
        fc_cols = []
        tour_n = 0
        players = []
        factions = Faction.load_factions(factions_fname)
        tables = set()
        with open(fname, 'r') as csvf:
            rdr = csv.reader(csvf)
            for i, l in enumerate(rdr):
                if i == 0:
                    tb_cols = [
                        i for i in range(len(l))
                        if l[i] in ['t', 'T', 'TB', 'Tb', 'tb']
                    ]
                    vp_cols = [
                        i for i in range(len(l))
                        if l[i] in ['v', 'V', 'VP', 'Vp', 'vp']
                    ]
                    nm_cols = [
                        i for i in range(len(l))
                        if l[i] in ['N', 'Name', 'Nick']
                    ]
                    fc_cols = [
                        i for i in range(len(l)) if l[i] in ['F', 'Faction']
                    ]
                    tour_n = len(tb_cols)
                    if len(vp_cols) < tour_n or len(vp_cols) > (tour_n + 1):
                        raise RuntimeError(
                            'Wrong tournament caption {}'.format(l))
                    continue

                name = l[nm_cols[0] if nm_cols else 1].strip()
                faction = None
                if fc_cols:
                    fc_key = l[fc_cols[0]].strip().lower()
                    faction = factions[fc_key].name
                tours = [(int(l[j]), int(l[k]))
                         for j, k in zip(tb_cols, vp_cols[:tour_n])]
                tables = tables.union(set([t[0] for t in tours]))
                players.append((i, name, faction, tours))

        tourney_factions = {}
        tourney_players = {}
        missing_players = []
        existing_players = Player.load_players(players_fname)
        for i, name, faction, _ in players:
            if name not in existing_players and name != 'Proxy':
                missing_players.append(name)

            tourney_players[i] = name
            if faction is not None:
                tourney_factions[i] = faction

        if missing_players:
            raise RuntimeError('Missing players: {}'.format(missing_players))

        gl = {}
        exec(
            'params = ({})'.format(
                os.path.splitext(os.path.basename(fname))[0]), gl)
        date, name, org, city, tt = gl['params']
        tourney = self.create(name, date, org, city, tt, tourney_players,
                              tourney_factions)

        if not tourney_factions:
            raise RuntimeError(
                'Tournament ({}) without specified factions'.format(name))

        for tour in range(tour_n):
            for t in sorted(tables):
                table = []
                for i, name, _, tours in players:
                    if name != 'Proxy' and tours[tour][0] == t:
                        table.append((i, tours[tour][1]))

                if len(table) < 2:
                    continue

                if len(table) > 2:
                    raise RuntimeError(
                        'Too many players on the same table (tour {}, table {})'
                        .format(tour, t))

                i1 = table[0][0]
                i2 = table[1][0]
                res = 1 if table[0][1] > table[1][1] else (
                    -1 if table[0][1] < table[1][1] else 0)
                tourney.add_match(i1, i2, res)

            tourney.end_current_tour()

    def load_league(self,
                    fname,
                    players_fname='players.csv',
                    factions_fname='factions.csv'):
        tourney = None
        tourney_players = {}
        missing_players = []
        existing_players = Player.load_players(players_fname)
        factions = Faction.load_factions(factions_fname)
        with open(fname, 'r') as csvf:
            rdr = csv.reader(csvf)
            for i, l in enumerate(rdr):
                if i == 0:
                    player_n = int(l[0])
                    continue

                if i <= player_n:
                    name = l[1].strip()

                    if name not in existing_players and name != 'Proxy':
                        missing_players.append(name)

                    tourney_players[l[0]] = name

                    if len(tourney_players) == player_n:
                        if missing_players:
                            raise RuntimeError(
                                'Missing players: {}'.format(missing_players))

                        gl = {}
                        exec(
                            'params = ({})'.format(
                                os.path.splitext(os.path.basename(fname))[0]),
                            gl)
                        date, name, org, city = gl['params']

                        tourney = self.create_league(name, date, org, city,
                                                     tourney_players)
                else:
                    p1, p2, year, month, day, f1, f2 = l[:7]

                    if p1 == '' or p2 == '':
                        continue

                    f1 = f1.strip().lower()
                    f1 = factions[f1].name if f1 in factions else None

                    f2 = f2.strip().lower()
                    f2 = factions[f2].name if f2 in factions else None

                    tourney.add_match(
                        p1, p2, 1,
                        datetime.date(int(year), int(month), int(day)), f1, f2)
