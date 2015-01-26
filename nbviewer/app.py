#-----------------------------------------------------------------------------
#  Copyright (C) 2013 The IPython Development Team
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

import os

from concurrent.futures import ThreadPoolExecutor

from tornado import web, httpserver, ioloop, log
from tornado.httpclient import AsyncHTTPClient

import tornado.options
from tornado.options import define, options

from jinja2 import Environment, FileSystemLoader

from IPython.config import Config
from IPython.nbconvert.exporters import HTMLExporter
from IPython.nbconvert.filters import markdown2html

from .handlers import handlers
from .cache import DummyAsyncCache, AsyncMultipartMemcache, pylibmc
from .github import AsyncGitHubClient

#-----------------------------------------------------------------------------
# Code
#-----------------------------------------------------------------------------

here = os.path.dirname(__file__)
pjoin = os.path.join

def nrhead():
    try:
        import newrelic.agent
    except ImportError:
        return ''
    return newrelic.agent.get_browser_timing_header()

def nrfoot():
    try:
        import newrelic.agent
    except ImportError:
        return ''
    return newrelic.agent.get_browser_timing_footer()

def main():
    # command-line options
    define("debug", default=False, help="run in debug mode", type=bool)
    define("port", default=5000, help="run on the given port", type=int)
    define("cache_expiry", default=10*60, help="cache timeout (seconds)", type=int)
    define("threads", default=1, help="number of threads to use for background IO", type=int)
    tornado.options.parse_command_line()
    
    # NBConvert config
    config = Config()
    config.HTMLExporter.template_file = 'basic'
    config.NbconvertApp.fileext = 'html'
    config.CSSHTMLHeaderTransformer.enabled = False
    # don't strip the files prefix - we use it for redirects
    # config.Exporter.filters = {'strip_files_prefix': lambda s: s}
    
    exporter = HTMLExporter(config=config)
    
    # setup memcache
    pool = ThreadPoolExecutor(options.threads)
    memcache_urls = os.environ.get('MEMCACHIER_SERVERS',
        os.environ.get('MEMCACHE_SERVERS')
    )
    if pylibmc and memcache_urls:
        kwargs = dict(pool=pool)
        username = os.environ.get('MEMCACHIER_USERNAME', '')
        password = os.environ.get('MEMCACHIER_PASSWORD', '')
        if username and password:
            kwargs['binary'] = True
            kwargs['username'] = username
            kwargs['password'] = password
            log.app_log.info("Using SASL memcache")
        else:
            log.app_log.info("Using plain memecache")
        
        cache = AsyncMultipartMemcache(memcache_urls.split(','), **kwargs)
    else:
        log.app_log.info("Using in-memory cache")
        cache = DummyAsyncCache()
    
    # setup tornado handlers and settings
    
    template_path = pjoin(here, 'templates')
    static_path = pjoin(here, 'static')
    env = Environment(loader=FileSystemLoader(template_path))
    env.filters['markdown'] = markdown2html
    env.globals.update(nrhead=nrhead, nrfoot=nrfoot)
    client = AsyncHTTPClient()
    github_client = AsyncGitHubClient(client)
    github_client.authenticate()
    
    settings = dict(
        jinja2_env=env,
        static_path=static_path,
        client=client,
        github_client=github_client,
        exporter=exporter,
        cache=cache,
        cache_expiry=options.cache_expiry,
        pool=pool,
    )
    
    # create and start the app
    app = web.Application(handlers, debug=options.debug, **settings)
    http_server = httpserver.HTTPServer(app)
    log.app_log.info("Listening on port %i", options.port)
    http_server.listen(options.port)
    ioloop.IOLoop.instance().start()
    

if __name__ == '__main__':
    main()
