# tm-bot

## Getting Started

This tutorial will help you run server locally

### Prerequisites

`Docker compose` is used to make it easier to start it. See the
official [docker installation documentation](https://docs.docker.com/compose/install/).

### Installation

Clone the repo

   ```sh
   git clone https://github.com/athlone-net/tm-bot.git
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
