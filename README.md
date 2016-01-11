# calvin

Script to download all comic strips from [@Calvinn_Hobbes](https://twitter.com/Calvinn_Hobbes) twitter account.

## Setup


```
git clone git@github.com:shagunsodhani/calvin.git

cd calvin

mkdir images

cp config/config.cfg.sample config/config.cfg
```

Update the fields in `config.cfg` and import schema from `schema`.

Run `python scrapper.py`. This will download 3200 most recent tweets. [@Calvinn_Hobbes](https://twitter.com/Calvinn_Hobbes) has made less than 3000 tweets as of now. So we will be able to collect all tweets. Setup `scrapper.py` to run as a cron job to download new tweets.

## License

[MIT](http://shagun.mit-license.org/)