#!/usr/bin/env python3
"""
Generate a test dataset.
"""

import random
import string

import lorem
import pymongo

import config
import structure
import utils


def make_description():
  """
  Make a random description based on lorem ipsum.

  Returns:
     str: a random description

  """
  desc = random.choice((lorem.sentence,
                        lorem.paragraph,
                        lorem.text))()
  desc.replace('\n', '<br/>')
  return desc


if __name__ == '__main__':
  conf = config.read_config()
  dbserver = pymongo.MongoClient(host=conf['mongo']['host'],
                                 port=conf['mongo']['port'],
                                 username=conf['mongo']['user'],
                                 password=conf['mongo']['password'])
  db = dbserver[conf['mongo']['db']]

  # datasets
  for i in range(1, 501):
    dataset = structure.dataset()
    changes = {'title': f'Dataset {i} Title',
               'description': make_description(),
               'dmp': f'https://dsw-url{i}',
               'creator': 'Facility ' + random.choice(string.ascii_uppercase),
               'data_urls': [{'description': f'Download location {j}',
                              'url': f'https://data_source{i}/{random.choice(string.ascii_uppercase)}'}
                             for j in range(1, random.randint(1, 6))]}
    dataset.update(changes)
    db['datasets'].insert_one(dataset)

  # users
  base = [{'name' : 'User Test', 'role' : 'User', 'email' : 'user@example.com',
           'country' : 'Sweden', 'affiliation' : 'Test university', 'auth_id' : 'hash3@elixir' },
          {'name' : 'Steward Test', 'role' : 'Steward', 'email' : 'steward@example.com',
           'country' : 'Sweden', 'affiliation' : 'Test university', 'auth_id' : 'hash2@elixir' },
          {'name' : 'Admin Test', 'role' : 'Admin', 'email' : 'admin@example.com',
           'country' : 'Sweden', 'affiliation' : 'Test university', 'auth_id' : 'hash1@elixir' }]
  db['users'].insert_many(base)
  countries = utils.country_list()
  for i in range(1,98):
    user = structure.user()
    changes = {'affiliation': 'University ' + random.choice(string.ascii_uppercase),
               'name': f'First Last {i}',
               'email': f'user{i}@place{i}',
               'country': random.choice(countries),
               'auth_id': f'hash{i}@elixir'}
    user.update(changes)
    db['users'].insert_one(user)

  # projects
  datasets = tuple(db['datasets'].find())
  users = tuple(db['users'].find())
  for i in range(1, 501):
    project = structure.project()
    changes = {'title': f'Project {i} Title',
               'description': make_description(),
               'owner': random.choice(users)['email'],
               'contact': f'email{i}@entity{i}',
               'datasets': [random.choice(datasets)['uuid'] for _ in range(random.randint(0, 5))]}
    project.update(changes)
    db['projects'].insert_one(project)

