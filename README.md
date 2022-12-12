# LectioCal

![License](https://img.shields.io/github/license/dnorhoj/LectioCal)
![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/dnorhoj/LectioCal)
![Codacy grade](https://img.shields.io/codacy/grade/76cecd863b67412fad55505149d99fce)

This small script lets you synchronize your lectio.dk schedule with any standard CalDAV server.

This has been developed and tested with `Python 3.10`. But it *should* work with any newer python 3 version.

## Table of Contents

- [LectioCal](#lectiocal)
  - [Table of Contents](#table-of-contents)
  - [Requirements](#requirements)
  - [Running](#running)
  - [Environment variables](#environment-variables)
  - [Team translations](#team-translations)
    - [Example configuration](#example-configuration)
  - [License](#license)
  - [Contributing](#contributing)

## Requirements

I recommend using `pipenv install`, but you can also install dependencies with pip;

```sh
pip install -r requirements.txt
```

## Running

The recommended way to run the script is with the docker image, which will run the script every hour. Please refer to the [docker hub repository](https://hub.docker.com/r/dnorhoj/lectiocal) for more information on how to customize it more. But to simply run the script you can execute the following `docker run` command:

```bash
docker run -d \
  --name lectiocal \
  --restart always \
  --env-file .env \
  dnorhoj/lectiocal:latest
```

You can also run this script with python, where you can run the script either a single time, with `python main.py`, or run the script every hour with `python schedule.py`

Moreover, you can build and run the repository as a docker image, use heroku, or run it with similar services.

## Environment variables

To use the script you need a few environment variables.

```env
LECTIO_INST_ID=123
LECTIO_USERNAME="exam123p"
LECTIO_PASSWORD="eX4mp13"

CALDAV_URL="https://example.com"
CALDAV_USERNAME="example@example.com"
CALDAV_PASSWORD="example"
```

## Team translations

Optionally, you can set up team translations.

To do this, you can create a file called `team_translations.json` in the root,
where you specify your team name translations.

Here you can define case insensitive name as key, which will be searched for,
the search is *case insensitive* and does not need a full match, to succeed.

### Example configuration

```json
{
  "da": "Dansk",
  "ma": "Math",
  "en": "Engelsk"
}
```

## License

This project uses the `GNU Lesser General Public License v3.0` license.

You can read more in [LICENSE](./LICENSE).

## Contributing

If you have any suggestions, bug reports or anything else, you can open an issue,
or fix it yourself and open a pull request. :)
