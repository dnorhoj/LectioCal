# LectioCal

![](https://img.shields.io/github/license/dnorhoj/LectioCal)

This small script lets you synchronize your lectio.dk schedule with any standard CalDAV server.

This has been developed and tested with `Python 3.10`. But it *should* work with any newer python 3 version.

## Requirements

I recommend using `pipenv install`, but you can also install dependencies with pip;

    pip install -r requirements.txt

## Environment variables

To use the script you need a few environment variables.

```
LECTIO_USERNAME="exam123p"
LECTIO_PASSWORD="eX4mp13"

CALDAV_URL="https://example.com"
CALDAV_USERNAME="example@example.com"
CALDAV_PASSWORD="example"
```

## License

This project uses the `GNU Lesser General Public License v3.0` license.

You can read more in [LICENSE](./LICENSE).

## Contributing

If you have any suggestions, bug reports or anything else, you can open an issue,
or fix it yourself and open a pull request. :)