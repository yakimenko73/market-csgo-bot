# <p align="center">Market csgo bot</p>

[![Pray for Ukraine](https://img.shields.io/badge/made_in-ukraine-ffd700.svg?labelColor=0057b7)](https://stand-with-ukraine.pp.ua)
[![Licence](https://img.shields.io/github/license/yakimenko73/market-csgo-bot)](https://github.com/yakimenko73/market-csgo-bot/blob/master/LICENSE)
[![Code factor](https://www.codefactor.io/repository/github/yakimenko73/market-csgo-bot/badge)](https://www.codefactor.io/repository/github/yakimenko73/market-csgo-bot)

## What is it?

Django app for managing and launching trading bots on `market.csgo`

### Built With

* [Python 3.x](https://www.python.org/)
* [Pydantic](https://github.com/pydantic/pydantic)
* [ELK](https://www.elastic.co/what-is/elk-stack)

## Getting started

### Prerequisites

`Docker compose` is used to make it easier to start it. See the
official [docker installation documentation](https://docs.docker.com/compose/install/).

### Installation

Clone the repo

   ```sh
   git clone https://github.com/yakimenko73/market-csgo-bot.git
   ```

Run with `docker-compose`

1. Create `.env.prod` file and fill it according to the `.env.dev`
    ```sh
    cat .env.dev >> .env.prod
    ```
2. Run `docker-compose`
   ```sh
   docker-compose --env-file .env.prod up --build
   ```
