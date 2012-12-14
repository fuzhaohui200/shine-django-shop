from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.utils import simplejson as json

from models import Continent, Country

def continent_json(request, continent_code):
    
    continent=get_object_or_404(Continent, code=continent_code)
    if not continent:
        raise Http404("Not implemented")
    countries = Country.objects.filter(continent=continent)
    context = {i.code: i.name for i in
               countries}

    callback = request.GET.get('callback', '')    
    if callback == '':
        data=json.dumps(context)
    else:
        data="callback(" + json.dumps(context) + ")"
    return HttpResponse(data, mimetype="application/json")

def country_json(request, continent_code, country_code):
    
    cont=get_object_or_404(Continent, code=continent_code)
    if not cont:
        raise Http404("Not implemented")
    country = get_object_or_404(Country, code=country_code)
    if not country:
        raise Http404("Not implemented")
    if country.continent != cont:
        raise Http404("Not implemented")

    context = {"area": country.area, "population": country.population, "capital": country.capital}
    callback = request.GET.get('callback', '')    
    if callback == '':
        data=json.dumps(context)
    else:
        data="callback(" + json.dumps(context) + ")"
    return HttpResponse(data, mimetype="application/json")


def show_continent(request, continent_code=None):
    context = {"all_continents": Continent.objects.all()}
    if continent_code:
        continent = get_object_or_404(Continent, code=continent_code)
        context["continent"] = continent
        countries = Country.objects.filter(continent=continent)
        context["countries"] = countries

    # Add your answer in 5.3 here
    if request.is_ajax():
        return render_to_response("countrydata/countrytable.html", context)
    return render_to_response("countrydata/index.html", context)

def render_javascript(request):
    """ NOTE: This is a really bad way of serving a static file! 
        It is only used in this exercise to serve this single JS file easily. """
    return render_to_response("countrydata/ajax_ui.js", mimetype="text/javascript")