from django.contrib import admin
from .models import Evento, Grupo, Area, Reuniao, Presenca, Posicao, Projeto, User, Links

class EventoAdmin(admin.ModelAdmin):
    filter_horizontal = ("membros_planejados",)

class ProjetoAdmin(admin.ModelAdmin):
    filter_horizontal = ("membros",)

class UserAdmin(admin.ModelAdmin):
    filter_horizontal = ("grupo", "area")

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Posicao)
admin.site.register(Grupo)
admin.site.register(Area)
admin.site.register(Projeto, ProjetoAdmin)
admin.site.register(Evento, EventoAdmin)
admin.site.register(Reuniao)
admin.site.register(Presenca)
admin.site.register(Links)

