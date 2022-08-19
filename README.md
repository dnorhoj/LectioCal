# LectioCal

![](https://img.shields.io/github/license/dnorhoj/LectioCal)
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
  - [Configuration](#configuration)
    - [Configuration options](#configuration-options)
  - [License](#license)
  - [Contributing](#contributing)

## Requirements

I recommend using `pipenv install`, but you can also install dependencies with pip;

    pip install -r requirements.txt

## Running

You can run the script either a single time, with `python main.py`, or you can run the script every hour with `python schedule.py`

Moreover, you can build and run the repository as a docker image, or use heroku, or similar services.

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

## Configuration

Configuration happens inside a `config.json` file in the root directory of the project.

*Note: you have to create this file yourself*

### Configuration options

<details>
  <summary>Team translations</summary> 

  Config: `team_translations`

  Lets you translate team names into a more readable form.

  If no translation is found, it will default to the original team name.

  **Format**

  | Name | Type | Default | Description |
  | - | - | - | - |
  | `match_full_team` | `bool` | `false` | If the translation key should be exact, or just be a part of module team |
  | `case_sensitive` | `bool` | `false` | Whether check should be case sensitive |
  | `translations` | `dict` (See example) | `{}` | Actual translation mapping |

  **Example configuration**
  ```json
  {
      "team_translations": {
          "match_full_team": false,
          "case_sensitive": false,
          "translations": {
              "DA": "Dansk",
              "MA": "Math",
              "EN": "Engelsk"
          }
      }
  }
  ```
</details>

## License

This project uses the `GNU Lesser General Public License v3.0` license.

You can read more in [LICENSE](./LICENSE).

## Contributing

If you have any suggestions, bug reports or anything else, you can open an issue,
or fix it yourself and open a pull request. :)
