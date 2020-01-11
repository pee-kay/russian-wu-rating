#!/usr/bin/env python
# -*- coding: utf-8 -*-

import trueskill
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
    def __init__(self, name, date, org, with_glass, players):
        self._name = name
        self._date = datetime.date(*date)
        self._org = org
        self._with_glass = with_glass
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

    def end_current_tour(self):
        self._matches.append([])

    def add_match(self, p1, p2, res=1):
        if res < 0:
            self._matches[-1].append((self._players[p2], self._players[p1], False))
        elif res == 0:
            self._matches[-1].append((self._players[p1], self._players[p2], True))
        else:
            self._matches[-1].append((self._players[p1], self._players[p2], False))

    def update_ratings(self, ratings, system = trueskill):
        for tour in self._matches:
            for (p1, p2, drawn) in tour:
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

            result.append((player, r.mu))

        return result

players_fname = 'players.csv'
players = Player.create_players(*load_players(players_fname).values())

tournaments = Tournaments()

# TODO: The Mirror Showdown - II 15.10.2018 https://docs.google.com/spreadsheets/d/1IgwytourneyzhfNlwKL7UMcBOYCVdzcAhp5Cfzkb_ueWN0gU/edit#gid=1317522882

# TODO: The Hunting Party - IX 24.12.2018 https://docs.google.com/spreadsheets/d/1xE529VWVc1zY3Sl1ck0f9jBFR2EqzpLWUSDOswMOX3Q/edit#gid=1317522882

tourney = tournaments.create(
    'The Mirror Showdown - III', (2019, 1, 20), 'Святослав Соколов', True, {
        'НЧ': 'Никита Чикулаев',
        'РЕ': 'Роман Евсеев',
        'ЕС': 'Евгений Сафронов',
        'ДН': 'Денис Никишин',
        'ЕО': 'Евгений Овчинников',
        'ЮА': 'Юлия Овчинникова',
        'СШ': 'Сергей Шевелев',
        'ПК': 'Павел Кузнецов',
        'АП': 'Алексей Павлов',
        'СБ': 'Soel',
        'АК': 'Анатолий Коновалов',
        'КК': 'Константин Кручинин',
        'ДТ': 'Дмитрий Точенов',
        'АД': 'Artur Diodand',
        'АС': 'Алексей Смышляев',
        'ФФ': 'Федор Федоренко',
        'ПФ': 'Петр Федин',
        'АМ': 'Андрей Морозов'
    })

# 1 тур
tourney.add_match('РЕ', 'КК', -1)
tourney.add_match('АК', 'АД', -1)
tourney.add_match('ДН', 'ЮА', 1)
tourney.add_match('ЕО', 'ЕС', -1)
tourney.add_match('ПК', 'ФФ', 1)
tourney.add_match('ПФ', 'АМ', 0)
tourney.add_match('НЧ', 'АП', 1)
tourney.add_match('АС', 'СБ', 0)
tourney.add_match('ДТ', 'СШ', -1)
tourney.end_current_tour()
# 2 тур
tourney.add_match('ПК', 'АД', -1)
tourney.add_match('ДН', 'КК', -1)
tourney.add_match('ЕС', 'СШ', 1)
tourney.add_match('НЧ', 'АС', 1)
tourney.add_match('ПФ', 'СБ', 1)
tourney.add_match('АМ', 'ФФ', -1)
tourney.add_match('АК', 'ЮА', 1)
tourney.add_match('РЕ', 'ЕО', 1)
tourney.add_match('ДТ', 'АП', 1)
tourney.end_current_tour()
# 3 тур
tourney.add_match('КК', 'АД', 0)
tourney.add_match('ЕС', 'НЧ', -1)
tourney.add_match('ПФ', 'АК', 0)
tourney.add_match('РЕ', 'ПК', -1)
tourney.add_match('ДН', 'ДТ', -1)
tourney.add_match('ФФ', 'СШ', 1)
tourney.add_match('АС', 'АМ', 1)
tourney.add_match('СБ', 'ЕО', 1)
tourney.end_current_tour()
# 4 тур
tourney.add_match('НЧ', 'КК', -1)
tourney.add_match('АД', 'ПФ', 1)
tourney.add_match('ПК', 'ДТ', 1)
tourney.add_match('ФФ', 'АК', 1)
tourney.add_match('ЕС', 'АС', 1)
tourney.add_match('РЕ', 'СБ', -1)
tourney.add_match('ДН', 'СШ', -1)
tourney.add_match('ЮА', 'АМ', 0)

tourney = tournaments.create(
    'Yermack\'s birthday cup', (2019, 1, 27), 'Роман Евсеев', True, {
        'КК': 'Константин Кручинин',
        'ДТ': 'Дмитрий Точенов',
        'ПФ': 'Петр Федин',
        'Сап': 'Сергей Сапожков',
        'АС': 'Александр Старовойтов',
        'ПК': 'Павел Кузнецов',
        'ВБ': 'Владимир Барсегов',
        'ЕК': 'Arsanar',
        'МК': 'Марк Карк',
        'СС': 'Святослав Соколов',
        'АК': 'Анатолий Коновалов',
        'ПА': 'Павел Аленчев',
        'СШ': 'Сергей Шевелев',
        'ГФ': 'Григорий Фисаков',
        'СБ': 'Soel',
        'ЕД': 'Егор Долженко',
        'ДН': 'Денис Никишин',
        'КМ': 'Кирилл Москаленко',
        'ВГ': 'Василий Гущин',
        'АП': 'Алексей Павлов',
        'МШ': 'Максим Шамцян'
    })

# 1 тур
tourney.add_match('КМ', 'АП', 1)
tourney.add_match('КК', 'ПК', 1)
tourney.add_match('ВБ', 'МШ', 1)
tourney.add_match('АС', 'МК', 1)
tourney.add_match('ЕК', 'ГФ', 1)
tourney.add_match('ЕД', 'ПА', 1)
tourney.add_match('ВГ', 'АК', -1)
tourney.add_match('СБ', 'СС', -1)
tourney.add_match('СШ', 'Сап', -1)
tourney.add_match('ДТ', 'ПФ', 1)
tourney.end_current_tour()
# 2 тур
tourney.add_match('КК', 'ЕК', 1)
tourney.add_match('ДТ', 'АК', 1)
tourney.add_match('Сап', 'ЕД', 1)
tourney.add_match('АС', 'ВБ', -1)
tourney.add_match('СС', 'КМ', 1)
tourney.add_match('ДН', 'СБ', 1)
tourney.add_match('АП', 'МШ', 1)
tourney.add_match('МК', 'СШ', 1)
tourney.add_match('ПА', 'ВГ', 1)
tourney.add_match('ПФ', 'ГФ', 1)
tourney.end_current_tour()
# 3 тур
tourney.add_match('КК', 'Сап', 1)
tourney.add_match('ДТ', 'СС', 1)
tourney.add_match('ВБ', 'ПА', 1)
tourney.add_match('ПФ', 'ДН', 1)
tourney.add_match('МК', 'АП', 1)
tourney.add_match('ГФ', 'ВГ', 1)
tourney.add_match('АС', 'ЕК', 1)
tourney.add_match('ПК', 'КМ', 1)
tourney.add_match('СБ', 'ЕД', 1)
tourney.add_match('СШ', 'МШ', 1)
tourney.end_current_tour()
# 4 тур
tourney.add_match('КК', 'ДТ', 1)
tourney.add_match('ПФ', 'ВБ', 1)
tourney.add_match('АС', 'МК', 1)
tourney.add_match('Сап', 'АК', 1)
tourney.add_match('ПК', 'СС', 1)
tourney.add_match('ПА', 'ДН', 1)
tourney.add_match('СШ', 'АП', 1)
tourney.add_match('СБ', 'КМ', 1)
tourney.add_match('ЕД', 'ЕК', -1)
tourney.add_match('ГФ', 'МШ', 1)

# TODO: попробовать добавить командник 'Shadeglass Crusade': https://docs.google.com/spreadsheets/d/1rdY1WNSRE1moKqVWZMxHGJlBaxPiC02wa-Ko5BeRo5M/edit#gid=0

tourney = tournaments.create(
    'The Hunting Party - X', (2019, 3, 31), 'Святослав Соколов', False, {
        'Ф': 'Константин Кручинин',
        'Н': 'Nevar',
        'ВВ': 'Владимир Владимирович',
        'НЧ': 'Никита Чикулаев',
        'ИМ': 'Иван Марков',
        'АК': 'Антон Корнаков',
        'МО': 'Максим Оргиец',
        'АлО': 'Александр Оводков',
        'АнО': 'Андрей Оводков',
        'АС': 'Алексей Смышляев',
        'МК': 'Михаил Ковальков',
        'АМ': 'Анна Мельникова',
        'ПФ': 'Петр Федин',
        'МА': 'Мирон Андреев'
    })

# 1 тур
tourney.add_match('Ф', 'МА', 1)
tourney.add_match('Н', 'ПФ', -1)
tourney.add_match('НЧ', 'МК', 1)
tourney.add_match('АМ', 'ВВ', 1)
tourney.add_match('АС', 'ИМ', 1)
tourney.add_match('АлО', 'МО', -1)
tourney.add_match('АнО', 'АК', 0)
tourney.end_current_tour()
# 2 тур
tourney.add_match('НЧ', 'ПФ', -1)
tourney.add_match('АС', 'АМ', 1)
tourney.add_match('Ф', 'МО', 1)
tourney.add_match('Н', 'ИМ', -1)
tourney.add_match('МК', 'АК', -1)
tourney.add_match('ВВ', 'МА', 1)
tourney.add_match('АнО', 'АлО', 1)
tourney.end_current_tour()
# 3 тур
tourney.add_match('АС', 'Ф', -1)
tourney.add_match('ПФ', 'АнО', 1)
tourney.add_match('НЧ', 'АК', 1)
tourney.add_match('АМ', 'ИМ', 0)
tourney.add_match('ВВ', 'МО', 1)
tourney.add_match('АлО', 'МК', 1)
tourney.add_match('МА', 'Н', -1)

tourney = tournaments.create(
    'The Hunting Party - XI', (2019, 4, 15), 'Святослав Соколов', False, {
        'КК': 'Константин Кручинин',
        'МК': 'Марк Карк',
        'ПМ': 'Полина Морозова',
        'ИМ': 'Иван Марков',
        'КБ': 'Кирилл Бадягин',
        'ВО': 'Владимир Осокин',
        'АО': 'Александр Оводков',
        'ВТ': 'Виталий Тютюриков'
    })

# 1 тур
tourney.add_match('АО', 'ПМ', 1)
tourney.add_match('ВТ', 'ИМ', -1)
tourney.add_match('ВО', 'КБ', -1)
tourney.add_match('МК', 'КК', 1)
tourney.end_current_tour()
# 2 тур
tourney.add_match('ИМ', 'АО', 1)
tourney.add_match('МК', 'КБ', 1)
tourney.add_match('ВТ', 'ПМ', 1)
tourney.add_match('ВО', 'КК', -1)
tourney.end_current_tour()
# 3 тур
tourney.add_match('ИМ', 'МК', -1)
tourney.add_match('АО', 'КК', -1)
tourney.add_match('КБ', 'ВТ', -1)
tourney.add_match('ПМ', 'ВО', -1)

tourney = tournaments.create(
    'The Hunting Party - XII', (2019, 5, 6), 'Святослав Соколов', False, {
        'ДТ': 'Дмитрий Точенов',
        'ВВ': 'Владимир Владимирович',
        'Ф': 'Faraicool',
        'МХ': 'Максим Халилулин',
        'АП': 'Александр Петрив',
        'АО': 'Александр Оводков',
        'ДМ': 'Дмитрий Матвеев',
        'Си': 'Виктор Нелипович',
        'Кр': 'Кронос',
        'Св': 'Свежеватель',
        'Й': 'YNot',
        'СС': 'Святослав Соколов'
    })

# 1 тур
tourney.add_match('ДТ', 'Й', 1)
tourney.add_match('ВВ', 'Св', 1)
tourney.add_match('Кр', 'Ф', 1)
tourney.add_match('МХ', 'Си', -1)
tourney.add_match('АП', 'ДМ', 1)
tourney.add_match('АО', 'СС', -1)
tourney.end_current_tour()
# 2 тур
tourney.add_match('Си', 'СС', -1)
tourney.add_match('ДТ', 'АП', 1)
tourney.add_match('ВВ', 'Кр', 1)
tourney.add_match('АО', 'МХ', -1)
tourney.add_match('Й', 'ДМ', -1)
tourney.add_match('Св', 'Ф', -1)
tourney.end_current_tour()
# 3 тур
tourney.add_match('СС', 'ВВ', 1)
tourney.add_match('ДТ', 'Си', -1)
tourney.add_match('МХ', 'АП', -1)
tourney.add_match('ДМ', 'Ф', 1)
tourney.add_match('Кр', 'Св', -1)
tourney.add_match('АО', 'Й', 1)

tourney = tournaments.create(
    'The Mirror Showdown - IV', (2019, 5, 27), 'Святослав Соколов', True, {
        'РЕ': 'Роман Евсеев',
        'АО': 'Александр Оводков',
        'СШ': 'Сергей Шевелев',
        'АП': 'Александр Петрив',
        'ДА': 'Данила Антонов',
        'ВВ': 'Владимир Владимирович',
        'ИМ': 'Иван Марков',
        'ЕК': 'Arsanar',
        'ДТ': 'Дмитрий Точенов',
        'ДУ': 'Денис Ульмаев',
        'МКа': 'Максим Каревский',
        'АКа': 'Александр Каревский',
        'АКу': 'Александр Кутлин',
        'ИК': 'Илья Кордонец',
        'СВ': 'Стас Водолазский',
        'МКо': 'Михаил Ковальков',
        'ПФ': 'Петр Федин',
        'ПА': 'Павел Аленчев',
        'МА': 'Мирон Андреев',
        'ВК': 'Виталий Кривошеев'
    })

# 1 тур
tourney.add_match('РЕ', 'ЕК', 1)
tourney.add_match('ВВ', 'АП', 1)
tourney.add_match('АО', 'АКа', -1)
tourney.add_match('СШ', 'ПФ', 0)
tourney.add_match('ИМ', 'ИК', 1)
tourney.add_match('ДТ', 'СВ', 1)
tourney.add_match('ДУ', 'МКо', -1)
tourney.add_match('ПА', 'МА', 1)
tourney.add_match('ДА', 'ВК', 1)
tourney.add_match('АКу', 'МКа', -1)
tourney.end_current_tour()
# 2 тур
tourney.add_match('ДА', 'РЕ', -1)
tourney.add_match('ИМ', 'МКа', -1)
tourney.add_match('ВВ', 'ПА', 1)
tourney.add_match('АКа', 'ДТ', -1)
tourney.add_match('МКо', 'ПФ', -1)
tourney.add_match('СШ', 'ДУ', 1)
tourney.add_match('СВ', 'АО', -1)
tourney.add_match('МА', 'АП', -1)
tourney.add_match('АКу', 'ИК', 1)
tourney.add_match('ЕК', 'ВК', 1)
tourney.end_current_tour()
# 3 тур
tourney.add_match('МКа', 'РЕ', -1)
tourney.add_match('ДТ', 'ВВ', 1)
tourney.add_match('СШ', 'ДА', 1)
tourney.add_match('ПФ', 'ЕК', 0)
tourney.add_match('ИМ', 'АП', -1)
tourney.add_match('ПА', 'АКа', -1)
tourney.add_match('АКу', 'МКо', -1)
tourney.add_match('АО', 'ВК', 1)
tourney.add_match('ДУ', 'МА', -1)
tourney.add_match('ИК', 'СВ', 0)
tourney.end_current_tour()
# 4 тур
tourney.add_match('ДТ', 'РЕ', 1)
tourney.add_match('СШ', 'МКа', 1)
tourney.add_match('АП', 'МКо', 1)
tourney.add_match('АКа', 'ПФ', -1)
tourney.add_match('АО', 'ВВ', -1)
tourney.add_match('ЕК', 'ДА', 1)
tourney.add_match('ИМ', 'ПА', 1)
tourney.add_match('МА', 'АКу', 1)
tourney.add_match('ИК', 'ДУ', 1)

tourney = tournaments.create(
    'The Heroes Of The Vault', (2019, 6, 9), 'Святослав Соколов', False, {
        'АС': 'Алексей Смышляев',
        'КК': 'Константин Кручинин',
        'ПФ': 'Петр Федин',
        'ДТ': 'Дмитрий Точенов',
        'СС': 'Святослав Соколов',
        'АО': 'Александр Оводков',
        'ЕК': 'Евгений Крамеров',
        'ВГ': 'Василий Гущин'
    })

# 1 тур
tourney.add_match('АС', 'СС', 1)
tourney.add_match('АО', 'ПФ', -1)
tourney.add_match('КК', 'ЕК', 1)
tourney.add_match('ВГ', 'ДТ', 0)
tourney.end_current_tour()
# 2 тур
tourney.add_match('КК', 'ПФ', 1)
tourney.add_match('АС', 'ДТ', 1)
tourney.add_match('ВГ', 'СС', -1)
tourney.add_match('АО', 'ЕК', 1)
tourney.end_current_tour()
# 3 тур
tourney.add_match('КК', 'АС', -1)
tourney.add_match('СС', 'ПФ', -1)
tourney.add_match('ДТ', 'АО', 1)
tourney.add_match('ВГ', 'ЕК', -1)

tourney = tournaments.create(
    'The Hunting Party - XIII', (2019, 6, 24), 'Святослав Соколов', False, {
        'СШ': 'Сергей Шевелев',
        'ВВ': 'Владимир Владимирович',
        'АС': 'Алексей Смышляев',
        'ИМ': 'Иван Марков',
        'ПА': 'Павел Аленчев',
        'ДМ': 'Дмитрий Матвеев',
        'ДУ': 'Денис Ульмаев',
        'ПФ': 'Петр Федин',
        'АЛ': 'Александр Лебедев',
        'ДА': 'Дарион'
    })

# 1 тур
tourney.add_match('ПА', 'ПФ', 1)
tourney.add_match('СШ', 'АС', 1)
tourney.add_match('ИМ', 'АЛ', 1)
tourney.add_match('ВВ', 'ДМ', 0)
tourney.add_match('ДУ', 'ДА', 1)
tourney.end_current_tour()
# 2 тур
tourney.add_match('ИМ', 'ДУ', 1)
tourney.add_match('СШ', 'ПА', 1)
tourney.add_match('ВВ', 'АЛ', 1)
tourney.add_match('ДМ', 'ДА', 1)
tourney.add_match('АС', 'ПФ', 1)
tourney.end_current_tour()
# 3 тур
tourney.add_match('ИМ', 'СШ', -1)
tourney.add_match('ВВ', 'ДУ', 1)
tourney.add_match('ДМ', 'АС', -1)
tourney.add_match('ПА', 'АЛ', 1)
tourney.add_match('ДА', 'ПФ', -1)

tourney = tournaments.create(
    'The Storming of The Mirrored City', (2019, 7, 15), 'Святослав Соколов', True, {
        'РЕ': 'Роман Евсеев',
        'ПФ': 'Петр Федин',
        'ПК': 'Павел Кузнецов',
        'ГГ': 'Глеб Гусев',
        'МО': 'Максим Оргиец',
        'ДН': 'Давид Нариманидзе',
        'ИМ': 'Иван Марков',
        'ЕТ': 'Евгений Тюляев',
        'ДК': 'Денис Кубиков',
        'ДТ': 'Дмитрий Точенов',
        'АМ': 'Анна Мельникова',
        'СС': 'Святослав Соколов'
    })

# 1 тур
tourney.add_match('ПК', 'ГГ', 0)
tourney.add_match('РЕ', 'ЕТ', 1)
tourney.add_match('ПФ', 'МО', 1)
tourney.add_match('ДН', 'СС', -1)
tourney.add_match('ИМ', 'АМ', -1)
tourney.add_match('ДТ', 'ДК', 1)
tourney.end_current_tour()
# 2 тур
tourney.add_match('СС', 'ДТ', 1)
tourney.add_match('РЕ', 'ПФ', -1)
tourney.add_match('ПК', 'АМ', 1)
tourney.add_match('ДН', 'ГГ', 0)
tourney.add_match('ДК', 'ЕТ', 1)
tourney.add_match('МО', 'ИМ', 1)
tourney.end_current_tour()
# 3 тур
tourney.add_match('СС', 'ПФ', -1)
tourney.add_match('ПК', 'ДТ', 1)
tourney.add_match('ДК', 'РЕ', -1)
tourney.add_match('МО', 'АМ', -1)
tourney.add_match('ДН', 'ИМ', 0)

tourney = tournaments.create(
    'The Hunting Party - XIV', (2019, 7, 28), 'Святослав Соколов', False, {
        'ПФ': 'Петр Федин',
        'АК': 'Антон Коняхин',
        'ВВ': 'Владимир Владимирович',
        'ДУ': 'Денис Ульмаев',
        'ДМ': 'Дмитрий Матвеев',
        'АЧ': 'Антон Чичеткин',
        'АА': 'Александр Алексеев',
        'ДК': 'Денис Кубиков',
        'АС': 'Алексей Смышляев',
        'МК': 'Михаил Ковальков'
    })

# 1 тур
tourney.add_match('ВВ', 'ДУ', 1)
tourney.add_match('ПФ', 'МК', 1)
tourney.add_match('АК', 'АА', -1)
tourney.add_match('ДМ', 'АС', -1)
tourney.add_match('АЧ', 'ДК', -1)
tourney.end_current_tour()
# 2 тур
tourney.add_match('ПФ', 'ДК', 1)
tourney.add_match('АС', 'ВВ', 1)
tourney.add_match('АА', 'МК', -1)
tourney.add_match('АЧ', 'ДМ', -1)
tourney.add_match('АК', 'ДУ', 1)
tourney.end_current_tour()
# 3 тур
tourney.add_match('ПФ', 'АС', 1)
tourney.add_match('АК', 'ДМ', -1)
tourney.add_match('МК', 'ДК', 1)
tourney.add_match('АА', 'ВВ', -1)
tourney.add_match('ДУ', 'АЧ', 1)

tourney = tournaments.create(
    'The Hunting Party - XV', (2019, 8, 1), 'Святослав Соколов', False, {
        'ДА': 'Давид Афинский',
        'АО': 'Александр Оводков',
        'ДВ': 'Ден Волк',
        'АА': 'Александр Алексеев',
        'АМ': 'Анна Мельникова',
        'СС': 'Святослав Соколов'
    })

# 1 тур
tourney.add_match('ДА', 'АО', -1)
tourney.add_match('ДВ', 'АА', -1)
tourney.add_match('АМ', 'СС', 1)
tourney.end_current_tour()
# 2 тур
tourney.add_match('АА', 'АМ', -1)
tourney.add_match('АО', 'ДВ', 1)
tourney.add_match('СС', 'ДА', 1)
tourney.end_current_tour()
# 3 тур
tourney.add_match('АМ', 'АО', 1)
tourney.add_match('СС', 'АА', -1)
tourney.add_match('ДА', 'ДВ', -1)

tourney = tournaments.create(
    'The Mirror Showdown - V', (2019, 8, 25), 'Святослав Соколов', True, {
        'ДК': 'Денис Кубиков',
        'АС': 'Алексей Смышляев',
        'ПФ': 'Петр Федин',
        'ДУ': 'Денис Ульмаев',
        'АА': 'Александр Алексеев',
        'МО': 'Максим Оргиец',
        'ДВ': 'Ден Волк',
        'ВТ': 'Виталий Тютюриков',
        'ДБ': 'Дмитрий Бондаренко',
        'АЧ': 'Антон Чичеткин',
        'ПК': 'Павел Кузнецов',
        'АК': 'Антон Коняхин',
        'ДТ': 'Дмитрий Точенов',
        'МЧ': 'Максим Чередников',
        'АМ': 'Анна Мельникова',
        'МФ': 'Максим Федоров'
    })

# 1 тур
tourney.add_match('ДК', 'АМ', -1)
tourney.add_match('АС', 'ПК', -1)
tourney.add_match('ПФ', 'ВТ', 1)
tourney.add_match('ДУ', 'МО', -1)
tourney.add_match('АА', 'ДВ', 0)
tourney.add_match('ДБ', 'АЧ', -1)
tourney.add_match('АК', 'ДТ', -1)
tourney.add_match('МФ', 'МЧ', 1)
tourney.end_current_tour()
# 2 тур
tourney.add_match('АЧ', 'АМ', -1)
tourney.add_match('ПК', 'ПФ', -1)
tourney.add_match('МФ', 'МО', 1)
tourney.add_match('ДТ', 'АА', 1)
tourney.add_match('ДВ', 'ДБ', 0)
tourney.add_match('ДК', 'АС', -1)
tourney.add_match('ВТ', 'МЧ', -1)
tourney.add_match('АК', 'ДУ', 1)
tourney.end_current_tour()
# 3 тур
tourney.add_match('ПФ', 'МФ', 1)
tourney.add_match('АМ', 'ДТ', -1)
tourney.add_match('АС', 'АЧ', 1)
tourney.add_match('ПК', 'АК', 1)
tourney.add_match('МЧ', 'ДВ', -1)
tourney.add_match('МО', 'АА', -1)
tourney.add_match('ДБ', 'ДК', -1)
tourney.add_match('ВТ', 'ДУ', -1)
tourney.end_current_tour()
# 4 тур
tourney.add_match('ПФ', 'ДТ', -1)
tourney.add_match('АС', 'АМ', 1)
tourney.add_match('ПК', 'МФ', 1)
tourney.add_match('ДК', 'АЧ', -1)
tourney.add_match('АК', 'МО', 0)
tourney.add_match('ДУ', 'ДБ', 0)

tourney = tournaments.create(
    'The Hunting Party - XVI', (2019, 9, 8), 'Святослав Соколов', False, {
        'ВВ': 'Владимир Владимирович',
        'МаК': 'Марк Карк',
        'ЕС': 'Евгений Сафронов',
        'ДМ': 'Дмитрий Матвеев',
        'МиК': 'Михаил Ковальков',
        'ДК': 'Денис Кубиков',
        'АК': 'Алексей Купляков',
        'ВН': 'Виктор Нелипович',
        'ВТ': 'Виталий Тютюриков',
        'СС': 'Святослав Соколов'
    })

# 1 тур
tourney.add_match('ВВ', 'МаК', -1)
tourney.add_match('ЕС', 'ДМ', 1)
tourney.add_match('МиК', 'ДК', 1)
tourney.add_match('АК', 'ВН', -1)
tourney.add_match('ВТ', 'СС', -1)
tourney.end_current_tour()
# 2 тур
tourney.add_match('СС', 'ВН', -1)
tourney.add_match('МиК', 'МаК', 1)
tourney.add_match('ЕС', 'ВТ', 1)
tourney.add_match('АК', 'ДМ', -1)
tourney.add_match('ВВ', 'ДК', 1)
tourney.end_current_tour()
# 3 тур
tourney.add_match('ЕС', 'ВН', 1)
tourney.add_match('МиК', 'СС', -1)
tourney.add_match('ВВ', 'ДМ', -1)
tourney.add_match('МаК', 'ДК', 1)

tourney = tournaments.create(
    'The Hunting Party - XVII', (2019, 9, 22), 'Святослав Соколов', False, {
        'АС': 'Алексей Смышляев',
        'АА': 'Александр Алексеев',
        'ДК': 'Денис Кубиков',
        'ПФ': 'Петр Федин',
        'АКо': 'Антон Коняхин',
        'МФ': 'Максим Федоров',
        'ЕО': 'Евгений Овчинников',
        'НЧ': 'Никита Чикулаев',
        'ВВ': 'Владимир Владимирович',
        'АЛ': 'Александр Лебедев',
        'Д': 'Дарион',
        'ГА': 'Григорий Архипов',
        'АКу': 'Алексей Купляков',
        'АМ': 'Алексей Меликянц',
        'ДМ': 'Дмитрий Матвеев',
        'СС': 'Святослав Соколов'
    })

# 1 тур
tourney.add_match('ПФ', 'НЧ', 1)
tourney.add_match('Д', 'ДМ', -1)
tourney.add_match('ВВ', 'МФ', -1)
tourney.add_match('АС', 'АА', -1)
tourney.add_match('ДК', 'АКо', 1)
tourney.add_match('АЛ', 'ЕО', -1)
tourney.add_match('ГА', 'АКу', -1)
tourney.add_match('АМ', 'СС', -1)
tourney.end_current_tour()
# 2 тур
tourney.add_match('ДК', 'СС', 1)
tourney.add_match('АА', 'ДМ', -1)
tourney.add_match('МФ', 'ЕО', -1)
tourney.add_match('АКу', 'ПФ', 1)
tourney.add_match('АКо', 'АМ', 1)
tourney.add_match('АС', 'Д', -1)
tourney.add_match('ВВ', 'АЛ', 1)
tourney.add_match('ГА', 'НЧ', -1)
tourney.end_current_tour()
# 3 тур
tourney.add_match('ДМ', 'ДК', 1)
tourney.add_match('ЕО', 'АКу', 1)
tourney.add_match('Д', 'СС', -1)
tourney.add_match('АКо', 'ВВ', -1)
tourney.add_match('АА', 'МФ', 1)
tourney.add_match('ПФ', 'АЛ', -1)
tourney.add_match('НЧ', 'АС', 1)
tourney.add_match('ГА', 'АМ', -1)
tourney.end_current_tour()
# 4 тур
tourney.add_match('ЕО', 'ДМ', 1)
tourney.add_match('ВВ', 'ДК', -1)
tourney.add_match('НЧ', 'АКу', 1)
tourney.add_match('АКо', 'МФ', -1)
tourney.add_match('АМ', 'Д', 1)
tourney.add_match('АС', 'ПФ', -1)

tourney = tournaments.create(
    'The Mirror Showdown - VI', (2019, 10, 20), 'Святослав Соколов', True, {
        'ПФ': 'Петр Федин',
        'СС': 'Степан Степанов',
        'ДК': 'Денис Кубиков',
        'ААл': 'Александр Алексеев',
        'НЧ': 'Никита Чикулаев',
        'АС': 'Алексей Смышляев',
        'ААн': 'Артем Анпилогов',
        'ВВ': 'Владимир Владимирович',
        'ДА': 'Данила Антонов',
        'МФ': 'Максим Федоров'
    })

# 1 тур
tourney.add_match('ПФ', 'МФ', 0)
tourney.add_match('СС', 'ДА', -1)
tourney.add_match('ДК', 'ААл', 1)
tourney.add_match('НЧ', 'ВВ', 1)
tourney.add_match('АС', 'ААн', 1)
tourney.end_current_tour()
# 2 тур
tourney.add_match('ДК', 'НЧ', 1)
tourney.add_match('ДА', 'АС', -1)
tourney.add_match('ПФ', 'ААл', 1)
tourney.add_match('МФ', 'ВВ', -1)
tourney.add_match('СС', 'ААн', -1)
tourney.end_current_tour()
# 3 тур
tourney.add_match('ДК', 'АС', 1)
tourney.add_match('ПФ', 'НЧ', 1)
tourney.add_match('ААн', 'ВВ', -1)
tourney.add_match('ДА', 'МФ', -1)
tourney.add_match('СС', 'ААл', -1)

tourney = tournaments.create(
    'MGT B-Day Party 2019', (2019, 12, 7), 'Святослав Соколов', True, {
        'ЕС': 'Евгений Сафронов',
        'МЯ': 'Максим Яцык',
        'НЧ': 'Никита Чикулаев',
        'ЕО': 'Евгений Овчинников',
        'КК': 'Константин Кручинин',
        'ПФ': 'Петр Федин',
        'ЛО': 'Леонид Овчинников',
        'АМ': 'Анна Мельникова',
        'МС': 'Михаил Соколов',
        'ПК': 'Павел Кузнецов',
        'МО': 'Максим Оргиец',
        'АШ': 'Ася Шестова',
        'АК': 'Анатолий Коновалов',
        'АЧ': 'Антон Чичеткин',
        'ДА': 'Данила Антонов',
        'АА': 'Александр Алексеев'
    })

# 1 тур
tourney.add_match('МЯ', 'АА', -1)
tourney.add_match('МС', 'АШ', 1)
tourney.add_match('ПФ', 'КК', 1)
tourney.add_match('ЕС', 'ДА', 1)
tourney.add_match('НЧ', 'ЛО', 1)
tourney.add_match('АМ', 'АК', -1)
tourney.add_match('ПК', 'МО', 1)
tourney.add_match('АЧ', 'ЕО', -1)
tourney.end_current_tour()
# 2 тур
tourney.add_match('ЕО', 'НЧ', -1)
tourney.add_match('ЕС', 'МС', 0)
tourney.add_match('ПК', 'ПФ', -1)
tourney.add_match('АК', 'АА', 1)
tourney.add_match('АЧ', 'ЛО', 1)
tourney.add_match('ДА', 'АШ', 1)
tourney.add_match('МО', 'КК', -1)
tourney.add_match('АМ', 'МЯ', 1)
tourney.end_current_tour()
# 3 тур
tourney.add_match('НЧ', 'ПФ', -1)
tourney.add_match('АК', 'ЕС', 0)
tourney.add_match('МС', 'АМ', -1)
tourney.add_match('КК', 'ЕО', 1)
tourney.add_match('АЧ', 'ПК', -1)
tourney.add_match('ДА', 'АА', 0)
tourney.add_match('ЛО', 'АШ', 1)
tourney.add_match('МЯ', 'МО', 0)

tourney = tournaments.create(
    'The Hunting Party - XVIII', (2019, 12, 22), 'Святослав Соколов', False, {
        'МФ': 'Максим Федоров',
        'ЕС': 'Евгений Сафронов',
        'КК': 'Константин Кручинин',
        'Д': 'Ден Волк',
        'НЧ': 'Никита Чикулаев',
        'ПК': 'Павел Кузнецов',
        'СС': 'Святослав Соколов',
        'МХ': 'Максим Халилулин'
    })

# 1 тур
tourney.add_match('МФ', 'НЧ', 1)
tourney.add_match('ЕС', 'СС', 0)
tourney.add_match('КК', 'МХ', 1)
tourney.add_match('Д', 'ПК', 0)
tourney.end_current_tour()
# 2 тур
tourney.add_match('МФ', 'КК', -1)
tourney.add_match('Д', 'СС', 0)
tourney.add_match('ПК', 'ЕС', 1)
tourney.add_match('НЧ', 'МХ', 1)
tourney.end_current_tour()
# 3 тур
tourney.add_match('КК', 'ПК', 1)
tourney.add_match('НЧ', 'Д', 1)
tourney.add_match('МФ', 'СС', 1)
tourney.add_match('ЕС', 'МХ', 1)

for tourney in tournaments:
    fname = '\'{}\', ({}, {}, {}), \'{}\', {}.csv'.format(tourney.name, tourney.date.year, tourney.date.month, tourney.date.day, tourney.org, tourney.with_glass)
    #with open(fname, 'w') as csvf:
    #    csvf.write('#,Name,')


for fname in glob.glob('tournaments/*.csv'):
    load_tournament(fname, tournaments, players_fname)

def main():
    print('Топ25 игроков России (по турнирам со стеклом)')
    print('=============================================')
    for i, (p, r) in enumerate(tournaments.rate_players(players, tourney_check = lambda t: t.with_glass)[:25]):
        print(str(i + 1).rjust(3), p.display.ljust(25), p.city.ljust(10), round(r, 2))
    print()
    '''
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
    print()'''

if __name__ == '__main__':
    main()