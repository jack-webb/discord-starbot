### Discord Starbot

A simple starboard/starbot for a Discord guild. Will listen for a given emoji on all messages in all channels, and post messages reaching a given threshold to a channel defined in the config.

#### Requirements and setup
_Requires Python 3.5.3 or later, Pipenv, and Postgresql_
1. Install dependencies with `pipenv install`
2. Copy `config.example.py` to `config.py` and add your bot token and database details.
3. Run with `pipenv run python -m main`
