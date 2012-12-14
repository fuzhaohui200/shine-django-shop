from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    #URL for getting JSON data for a given continent code (ex 5.2)
    (r"^data/(\w{2}).json",         continent_json),

    #URL for getting JSON data for a given country codes (in given continent) (ex 5.2)
    (r"^data/(\w{2})/(\w{2}).json", country_json),

    #URL for getting HTML page with list of continents (ex 5.3)
    (r"^$",                         show_continent),
    #URL for getting HTML partial page for a given continent (ex 5.3)
    (r"^(\w{2}).html$",             show_continent),
    
    #URL for getting the ajax file
    #NOTE: this is not the way to get static files it in real environments
    (r"^js/ajax_ui.js",             render_javascript),
)