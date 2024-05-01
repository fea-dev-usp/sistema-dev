from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
import json
from calendar import Calendar, month_name
import datetime as dt
import locale

locale.setlocale(locale.LC_TIME, 'pt_BR.utf-8')

from .models import User, Grupo, Area, Evento, Projeto, Presenca, Posicao, Reuniao, Links

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

# Create your views here.
@login_required(login_url="login")
def index(request):
    projetos = Projeto.objects.all().order_by("-dia_inicio")[:10]
    eventos = Evento.objects.all().order_by("-dia_inicio")[:10]
    grupos = Grupo.objects.all().order_by("dia_reuniao")
    areas = Area.objects.all().order_by("dia_reuniao")
    links = Links.objects.all()

    areas_grupos = list(areas) + list(grupos)

    return render(request, "sistema/index.html", {
        "projetos": projetos,
        "eventos": eventos,
        "reunioes": areas_grupos, 
        "links": links
    })
    
    
@login_required(login_url="login")
def ranking(request):
    users = enumerate(User.objects.all().order_by("-score"))
    return render(request, "sistema/ranking.html", {
        "members": users
        })

@login_required(login_url="login")
def search(request):
    search = request.GET.get("q")
    if search:
        projects = Projeto.objects.filter(nome__icontains=search).order_by("-dia_inicio")
        events = Evento.objects.filter(nome__icontains=search).order_by("-dia_inicio")
        users = User.objects.filter(username__icontains=search)
        return render(request, "sistema/search.html", {
            "projects": projects,
            "events": events,
            "users": users
        })
    else:
        return HttpResponseRedirect(reverse("index"))

@login_required(login_url="login")
def profile(request):
    user = User.objects.get(pk=request.user.id)
    cargo = str(user.posicao.nome)
    projetos = Projeto.objects.filter(membros=request.user).order_by("-dia_inicio")
    eventos = Evento.objects.filter(membros_planejados=request.user).order_by("-dia_inicio")
    presenca = Presenca.objects.filter(membro=request.user)

    user.score = 0
    for pres in presenca:
        user.score += pres.status_presenca
    user.score += projetos.count()
    user.score += eventos.count()
    user.save()

    return render(request, "sistema/profile.html", {
        "score": user.score,
        "cargo": cargo,
        "grupo": request.user.grupo.all(),
        "area": request.user.area.all(),
        "projects": projetos,
        "events": eventos,
    })

@csrf_exempt
@login_required(login_url="login")
def bio(request):
    if request.method == "POST":
        data = json.loads(request.body)
        text = data.get("text")
        
        if text == "":
            return JsonResponse({"message": "Biografia não pode estar vazia."})
        
        if text:
            user = User.objects.get(pk=request.user.id)
            user.biografia = text
            user.save()
        else:
            return JsonResponse({"message": "Biografia não pode estar vazia."})

        return JsonResponse({"message": "Biografia salva."})
    return render(request, "sistema/profile.html")


@csrf_exempt
@login_required(login_url="login")
def display(request, id, type_info):
    if request.method == "POST":
        data = json.loads(request.body)
        text = data.get("text")
        typeinfo = data.get("type")

        if not text or text == "":
            return JsonResponse({"message": "Campo de texto não pode estar vazio."})
        
        if typeinfo == "project":
            project = Projeto.objects.get(pk=id)
            project.descricao = text
            project.save()
            return JsonResponse({"message": "Você atualizou a descrição deste projeto."})
        elif typeinfo == "event":
            event = Evento.objects.get(pk=id)
            event.descricao = text
            event.save()
            return JsonResponse({"message": "Você atualizou a descrição deste evento."})
        else:
            return JsonResponse({"message": "Tipo inválido."})
    if type_info == "project":
        project = Projeto.objects.get(pk=id)
        return render(request, "sistema/display.html", {
            "info": project,
            "type": "project"
        })
    elif type_info == "event":
        event = Evento.objects.get(pk=id)
        return render(request, "sistema/display.html", {
            "info": event,
            "type": "event"
        })
    else:
        return render(request, "sistema/display.html", {
            "message": "Não foi encontrado."
        })
    
@login_required(login_url="login")
def meeting(request):
    cargo = str(request.user.posicao.nome)

    cargo_valor = POSICOES.get(cargo, 0)

    if cargo_valor < 3 and cargo_valor == 7:
        return render(request, "sistema/meeting.html", {
            "message": "Você não tem acesso a está página."
        })

    else:
        groups = list(Grupo.objects.all())
        areas = list(Area.objects.all())
        return render(request, "sistema/meeting.html", {
            "group_list": groups,
            "area_list": areas,
        })

@csrf_exempt
@login_required(login_url="login")
def meeting_duration(request, reuniao_id, type_info):
    if request.method == "POST":
        duration = request.POST.get('duration')
        members = request.POST.get('members').split(',')
        report = request.FILES.get('report')
        
        if members == ['']:
            return JsonResponse({"message": "Por favor selecione os membros."})

        reuniao = Reuniao(duracao=duration)

        if type_info == 'rp':
            reuniao.grupo = Grupo.objects.get(pk=reuniao_id)
            reuniao.tipo = type_info
        elif type_info == 'ra':
            reuniao.area = Area.objects.get(pk=reuniao_id)
            reuniao.tipo = type_info
        elif type_info == 'rd' or type_info == 'rg':
            reuniao.tipo = type_info
        else:
            return JsonResponse({"message": "Tipo de reunião inválida."})

        if report:
            reuniao.relatorio = report

        reuniao.save()

        propria_pessoa = False
        for member in members:
            presenca = Presenca(reuniao=reuniao)
            presenca.membro = User.objects.get(pk=int(member.split('_')[0]))
            presenca.status_presenca = float(member.split('_')[1])
            if presenca.membro == request.user:
                if presenca.status_presenca != 1.0:
                    presenca.status_presenca = 1.0
                propria_pessoa = True
            user = User.objects.get(pk=int(member.split('_')[0]))
            user.score += presenca.status_presenca
            user.save()
            presenca.save()

        if not propria_pessoa:
            presenca = Presenca(reuniao=reuniao)
            presenca.membro = request.user
            presenca.status_presenca = 1.0
            request.user.score += 1.0
            request.user.save()
            presenca.save()

        return JsonResponse({"message": "Reunião finalizada com sucesso."})
    else:
        if type_info == "rp":
            reuniao = Grupo.objects.get(pk=reuniao_id)
            usuarios = User.objects.filter(grupo=reuniao)
        elif type_info == "ra":
            reuniao = Area.objects.get(pk=reuniao_id)
            usuarios = User.objects.filter(area=reuniao)
        elif type_info == "rd":
            reuniao = "Reunião de Direção"
            usuarios = User.objects.filter(posicao__nome__in=["diretor", "vice-presidente", "presidente", "lider"])
        elif type_info == "rg":
            reuniao = "Reunião Geral"
            usuarios = User.objects.all()
        else:
            return render(request, "sistema/meeting_duration.html", {
                "message": "Não foi encontrado."
            })
        return render(request, "sistema/meeting_duration.html", {
            "membros": usuarios,
            "reuniao": reuniao,
            "reuniao_id": reuniao_id,
            "type_info": type_info
        })

@login_required(login_url="login")
def calendar(request):
    month = dt.datetime.now().month
    year = dt.datetime.now().year
    cal = Calendar().monthdays2calendar(year, month)

    def create_dict(queryset, key_name):
        result_dict = {}
        for item in queryset:
            if key_name == "dia_inicio":
                day_str = str(item.dia_inicio.day)
            elif key_name == "dia_reuniao":
                day_str = str(item.dia_reuniao)
            result_dict.setdefault(day_str, []).append(item)
        return result_dict

    events = Evento.objects.filter(dia_inicio__month=month, dia_inicio__year=year).order_by("dia_inicio")
    projects = Projeto.objects.filter(dia_inicio__month=month, dia_inicio__year=year).order_by("dia_inicio")
    areas = Area.objects.all().order_by("dia_reuniao")
    groups = Grupo.objects.all().order_by("dia_reuniao")

    event_dict = create_dict(events, "dia_inicio")
    project_dict = create_dict(projects, "dia_inicio")
    area_dict = create_dict(areas, "dia_reuniao")
    group_dict = create_dict(groups, "dia_reuniao")

    all_dict = {
        "events": event_dict,
        "projects": project_dict,
        "areas": area_dict,
        "groups": group_dict
    }

    return render(request, "sistema/calendar.html", {
        "calendar": cal,
        "month": month_name[month],
        "year": year,
        "all_dict": all_dict,
        "group_dict": group_dict,
        "area_dict": area_dict,
        "event_dict": event_dict,
        "project_dict": project_dict
    })

@login_required(login_url="login")
def create_view(request, intention):
    if request.user.is_staff:
        if intention == "user":
            groups = Grupo.objects.all()
            areas = Area.objects.all()
            positions = Posicao.objects.all()
            return render(request, "sistema/create.html", {
                "intention": intention,
                "groups": groups,
                "areas": areas,
                "positions": positions
            })
        elif intention == "event":
            areas = Area.objects.all()
            members = User.objects.all()
            return render(request, "sistema/create.html", {
                "intention": intention,
                "areas": areas,
                "members": members
            })
        elif intention == "project":
            groups = Grupo.objects.all()
            members = User.objects.all()
            return render(request, "sistema/create.html", {
                "intention": intention,
                "groups": groups,
                "members": members
            })
        else:
            return render(request, "sistema/create.html", {
            "message": intention
        })
    else:
        return render(request, "sistema/create.html", {
            "message": intention
        })


@login_required(login_url="login")
def create(request, intention):
    if request.method == "POST":
        if intention == "user":
            username = request.POST["username"]
            is_staff = request.POST.get("staff", False)
            email = request.POST["email"]
            group = request.POST["group"]
            area = request.POST["area"]
            position = request.POST["position"]
            
            # Ensure password matches confirmation
            password = request.POST["password"]
            confirmation = request.POST["confirmation"]

            if not username or not email or not group or not area or not position:
                error_message = "Por favor preencha todos os campos."
            elif password != confirmation:
                error_message = "Senha deve ser igual a confirmação."
            else:
                error_message = None
            groups = Grupo.objects.all()
            areas = Area.objects.all()
            positions = Posicao.objects.all()
            members = User.objects.all()

            if error_message:
                return render(request, "sistema/create.html", {
                    "message_error": error_message,
                    "intention": intention,
                    "groups": groups,
                    "areas": areas,
                    "positions": positions,
                    "members": members
                })
            
            if is_staff:
                is_staff = True
            
            group = Grupo.objects.get(pk=group)
            area = Area.objects.get(pk=area)
            position = Posicao.objects.get(pk=position)

            try:
                user = User.objects.create_user(username=username, email=email, password=password, is_staff=is_staff)

                user.grupo.set([group])
                user.area.set([area])
                user.posicao.set([position])

                user.save()
            except IntegrityError:
                groups = Grupo.objects.all()
                areas = Area.objects.all()
                positions = Posicao.objects.all()
                members = User.objects.all()
                return render(request, "sistema/create.html", {
                    "message_error": "Nome de usuário já existe.",
                    "intention": intention,
                    "groups": groups,
                    "areas": areas,
                    "positions": positions,
                    "members": members
                })

            return render(request, "sistema/create.html", {
                    "message_error": "Usuário criado.",
                    "intention": intention,
                    "groups": groups,
                    "areas": areas,
                    "positions": positions,
                    "members": members
                })
        
        elif intention == "project":
            name = request.POST["name"]
            description = request.POST["description"]
            group = request.POST["group"]
            category = request.POST["category"]
            start_date = request.POST["start-date"]
            start_time = request.POST["start-time"]
            end_date = request.POST["end-date"]
            end_time = request.POST["end-time"]
            members_project = request.POST.getlist("members")

            if not name or not description or not group or not start_date or not start_time or not members_project:
                error_message = "Preencha todos os campos. Até pelo menos um membro."
            elif end_date:
                if start_date > end_date:
                    error_message = "O dia inicial deve ser antes."
                elif start_date == end_date and (start_time > end_time or start_time == end_time):
                    error_message = "O dia final deve ser depois."
                else:
                    end_date_time = dt.datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M")
                    error_message = None
            elif not end_date and end_time:
                error_message = "Preencha o dia final."
            else:
                error_message = None
            
            groups = Grupo.objects.all()
            members = User.objects.all()

            if error_message:
                return render(request, "sistema/create.html", {
                    "message_error": error_message,
                    "intention": intention,
                    "groups": groups,
                    "members": members
                })
            
            start_date_time = dt.datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
            group = Grupo.objects.get(pk=group)
            
            project = Projeto.objects.create(nome=name, responsavel=request.user, descricao=description, grupo=group, dia_inicio=start_date_time)
            if category:
                project.categoria = category
            if end_date:
                project.dia_fim = end_date_time
            project.membros.set(members_project)

            for member in members_project:
                user = User.objects.get(pk=member)
                user.score += 1
                user.save()

            project.save()

            return render(request, "sistema/create.html", {
                "message_error": "Projeto criado.",
                "intention": intention,
                "groups": groups,
                "members": members
            })
        
        elif intention == "event":
            name = request.POST["name"]
            description = request.POST["description"]
            area = request.POST["area"]
            category = request.POST["category"]
            start_date = request.POST["start-date"]
            start_time = request.POST["start-time"]
            end_date = request.POST["end-date"]
            end_time = request.POST["end-time"]
            members_event = request.POST.getlist("members")

            if not name or not description or not area or not start_date or not start_time or not members_event:
                error_message = "Preencha todos os campos. Até pelo menos um membro."
            elif end_date:
                if start_date > end_date:
                    error_message = "O dia inicial deve ser antes."
                elif start_date == end_date and (start_time > end_time or start_time == end_time):
                    error_message = "O dia final deve ser depois."
                else:
                    end_date_time = dt.datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M")
                    error_message = None
            elif not end_date and end_time:
                error_message = "Preencha o dia final."
            else:
                error_message = None
                

            areas = Area.objects.all()
            members = User.objects.all()

            if error_message:
                return render(request, "sistema/create.html", {
                    "message_error": error_message,
                    "intention": intention,
                    "areas": areas,
                    "members": members
                })
            
            start_date_time = dt.datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
            area = Area.objects.get(pk=area)
            
            event = Evento.objects.create(nome=name, responsavel=request.user, descricao=description, area=area, dia_inicio=start_date_time)
            if category:
                event.categoria = category
            if end_date:
                event.dia_fim = end_date_time

            event.membros_planejados.set(members_event)
            for member in members_event:
                user = User.objects.get(pk=member)
                user.score += 1
                user.save()

            event.save()

            return render(request, "sistema/create.html", {
                    "message_error": "Evento criado.",
                    "intention": intention,
                    "areas": areas,
                    "members": members
                })
    return HttpResponseRedirect(reverse('create_view', args=[intention]))

def login_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        senha = request.POST["password"]
        
        try:
            username = User.objects.get(email=email).username
        except User.DoesNotExist:
            return render(request, "sistema/login.html", {
                "mensagem": "Usuário e/ou senha inválidos."
            })
        
        user = authenticate(request, username=username, password=senha)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "sistema/login.html", {
                "mensagem": "Usuário e/ou senha inválidos."
            })
    else:
        if request.user.is_authenticated:
            logout(request)
        return render(request, "sistema/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))