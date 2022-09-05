[![SWUbanner](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner2-direct.svg)](https://github.com/vshymanskyy/StandWithUkraine/blob/main/docs/README.md)
# Django elk stack

## What is it?

Django project template with elk stack. Inspired by [deviantony](https://github.com/deviantony/docker-elk)

### Built With

* [ELK](https://www.elastic.co/what-is/elk-stack/)
* [Django](https://www.djangoproject.com/)
* [Gunicorn](https://gunicorn.org/)

## Getting Started

This tutorial will help you run server locally

### Prerequisites

`Docker compose` is used to make it easier to start it. See the
official [docker installation documentation](https://docs.docker.com/compose/install/).

### Installation

Clone the repo

   ```sh
   git clone https://github.com/yakimenko73/django-elk.git
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

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any
contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also
simply open an issue with the tag "enhancement". Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/amazing-feature`)
3. Commit your Changes (`git commit -m 'Add some amazing-feature'`)
4. Push to the Branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Contact

* Twitter - [@masterslave_](https://twitter.com/masterslave_)
* Email - r.yakimenko.73@gmail.com
