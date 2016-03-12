# Jupyter Notebook Viewer
[![Gitter](https://badges.gitter.im/Join Chat.svg)](https://gitter.im/jupyter/nbviewer?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Jupyter nbviewer is the web application behind [The Jupyter Notebook Viewer](http://nbviewer.ipython.org), which is graciously hosted by [Rackspace](https://developer.rackspace.com/?nbviewer=awesome).

Run this locally to get most of the features of nbviewer on your own network.


## Quick Run

If you have `docker` installed, you can pull and run the currently built version of the Docker container by

```shell
$ docker pull jupyter/nbviewer
$ docker run -p 8080:8080 jupyter/nbviewer
```

It automatically gets built with each push to `master`, so you'll always be able to get the freshest copy.

For speed and friendliness to GitHub, be sure to set `GITHUB_OAUTH_KEY` and `GITHUB_OAUTH_SECRET`:

```shell
$ docker run -p 8080:8080 -e 'GITHUB_OAUTH_KEY=YOURKEY' \
                          -e 'GITHUB_OAUTH_SECRET=YOURSECRET' \
                          jupyter/nbviewer
```

Or to use your GitHub personal access token, you can set just `GITHUB_API_TOKEN`.


## GitHub Enterprise

To use nbviewer on against your own GitHub Enterprise instance you need to set `GITHUB_API_URL`.
The relevant [API endpoints for GitHub Enterprise](https://developer.github.com/v3/enterprise/) are prefixed with `http://hostname/api/v3`.
You must also specify your `OAUTH` or `API_TOKEN` as explained above.  For example:

```shell
$ docker run -p 8080:8080 -e 'GITHUB_OAUTH_KEY=YOURKEY' \
                          -e 'GITHUB_OAUTH_SECRET=YOURSECRET' \
                          -e 'GITHUB_API_URL=https://ghe.example.com/api/v3/' \
                          jupyter/nbviewer
```

With this configured all GitHub API requests will go to you Enterprise instance so you can view all of your internal notebooks.

## Local Development

### With Docker

You can build a docker image that uses your local branch


#### Build

```shell
docker build -t nbviewer .
```


#### Run

```shell
docker run -p 8080:8080 nbviewer
```


### Local Installation

The Notebook Viewer requires several binary packages to be installed on your system. The primary ones are `libmemcached-dev libcurl4-openssl-dev pandoc libevent-dev`. Package names may differ on your system, see [salt-states](https://github.com/rgbkrk/salt-states-nbviewer/blob/master/nbviewer/init.sls) for more details.

If they are installed, you can install the required Python packages via pip.

```shell
pip install -r requirements.txt`
```


#### Static Assets

Static assets are maintained with `bower` and `less`.

```shell
$ cd <path to repo>
$ invoke bower
$ invoke less [-d]
```

This will download the relevant assets into `nbviewer/static/components` and create the built assets in `nbviewer/static/build`.

Pass `-d` or `--debug` to `invoke less` to create a CSS sourcemap, useful for debugging.


#### Running Locally

```shell
$ cd <path to repo>
$ python -m nbviewer --debug --no-cache
```

This will automatically relaunch the server if a change is detected on a python file, and not cache any results. You can then just do the modifications you like to the source code and/or the templates then refresh the pages.
