from django import template
from calendar import day_name
import locale

locale.setlocale(locale.LC_TIME, 'pt_BR.utf-8')

register = template.Library()

POSICOES = {
    "trainee": 1,
    "membro": 2, 
    "diretor": 3,    
    "lider": 4,    
    "vice-presidente": 5,
    "presidente": 6,
    "ex-membro": 7,
    "fundador": 8,
}

@register.filter
def get_week_name(week_day):
    return day_name[int(week_day)].encode("latin1").decode("utf-8").capitalize()

@register.filter
def enumerate_for(lista):
    return enumerate(lista)

@register.filter
def lenght_last(indice, lista):
    return indice + 1 != len(lista)

@register.filter
def lenght_for(lista):
    return len(lista) > 1

@register.filter
def get_item(dictionary, key):
    return dictionary.get(str(key))

@register.filter
def iterarate_key(dictionary):
    return dictionary.keys()

@register.filter
def get_item_ava(dictionary, key):
    return dictionary.get(key)

@register.filter
def verify(dictionary, key):
    return str(key) in dictionary

@register.filter
def verify_item_dict(dictionary, key):
    if key in dictionary:
        return dictionary.get(key)
    else:
        return None
    
@register.filter
def get_all(manytomany):
    return manytomany.all()

@register.simple_tag
def verify_events(dictionary, keyweek, keyday):
    count = 0
    points_group_area = {
        "areas": 2,
        "groups": 1
    }
    points_project_event = {
        "events": 11,
        "projects": 5,
    }
    for event in dictionary:
        if event in points_group_area and str(keyweek) in dictionary[event]:
            count += points_group_area.get(event, 0)
        if event in points_project_event and str(keyday) in dictionary[event]:
            count += points_project_event.get(event, 0)
            
    return count

@register.filter
def get_list(key):
    cargo_valor = POSICOES.get(str(key), 0)
    return cargo_valor > 2 and cargo_valor != 7