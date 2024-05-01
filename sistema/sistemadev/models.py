from django.db import models
from django.contrib.auth.models import AbstractUser

ia = "Inteligência Artificial"
cg = "Contgramação"
fq = "Finanças Quantitativas"
dw = "Desenvolvimento Web"
of = "The Office"

ESCOLHAS_GRUPO = (
    (ia, "Inteligência Artificial"),
    (cg, "Contgramação"),
    (fq, "Finanças Quantitativas"),
    (dw, "Desenvolvimento Web"),
    (of, "The Office"),
)

rh = "Recursos Humanos"
mkt = "Marketing"
projetos = "Projetos"

ESCOLHAS_AREA = (
    (rh, "Recursos Humanos"),
    (mkt, "Marketing"),
    (projetos, "Projetos"),
)

REUNIOES = (
    ("rd", "Reunião Diretoria"),
    ("rg", "Reunião Geral"),
    ("ra", "Reunião Área"),
    ("rp", "Reunião Grupo"),
)

DIAS_SEMANA = (
    ("0", "Segunda"),
    ("1", "Terça"),
    ("2", "Quarta"),
    ("3", "Quinta"),
    ("4", "Sexta"),
    ("5", "Sábado"),
    ("6", "Domingo"),
)

POSICOES = (
    ("membro", "Membro"),
    ("trainee", "Trainee"),
    ("diretor", "Diretor"),
    ("lider", "Líder"),
    ("vice-presidente", "Vice-Presidente"),
    ("presidente", "Presidente"),
    ("ex-membro", "Ex-Membro"),
    ("fundador", "Fundador"),
)

PRESENCA = (
        (-0.5, "Confirmou presença e não foi"),
        (0.0, "Ausente"),
        (0.3, "Ausente com justificativa"),
        (1.0, "Presente"),
    )

# Crie seus modelos aqui.
class Grupo(models.Model):
    nome = models.CharField(max_length=30, choices=ESCOLHAS_GRUPO)
    descricao = models.TextField(max_length=500, blank=True, null=True)
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    dia_reuniao = models.CharField(max_length=20, choices=DIAS_SEMANA)
    lider = models.ForeignKey("User", on_delete=models.CASCADE, related_name="lider_grupo", blank=True, null=True)

    def __str__(self):
        return f"{self.nome}"

class Area(models.Model):
    nome = models.CharField(max_length=30, choices=ESCOLHAS_AREA)
    descricao = models.TextField(max_length=500, blank=True, null=True)
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    dia_reuniao = models.CharField(max_length=20, choices=DIAS_SEMANA)
    diretor = models.ForeignKey("User", on_delete=models.CASCADE, related_name="diretor_area", blank=True, null=True)

    def __str__(self):
        return f"{self.nome}"

class Posicao(models.Model):
    nome = models.CharField(max_length=30, choices=POSICOES)
    descricao = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.nome}"

class User(AbstractUser):
    posicao = models.ForeignKey("Posicao",on_delete=models.CASCADE, related_name="posicao_usuario")
    grupo = models.ManyToManyField("Grupo", related_name="grupo_usuario", blank=True)
    area = models.ManyToManyField("Area", related_name="area_usuario", blank=True)
    biografia = models.TextField(max_length=250, blank=True, null=True)
    score = models.FloatField(default=0)

    def __str__(self):
        return f"{self.username}"

class Evento(models.Model):
    area = models.ForeignKey("Area", on_delete=models.CASCADE, related_name="area_evento")
    responsavel = models.ForeignKey("User", on_delete=models.CASCADE, related_name="responsavel_evento")
    membros_planejados = models.ManyToManyField("User", blank=True, related_name="membros_planejados_evento")
    nome = models.CharField(max_length=50)
    descricao = models.TextField(max_length=500)
    dia_inicio = models.DateTimeField()
    dia_fim = models.DateTimeField(blank=True, null=True)
    criado = models.DateTimeField(auto_now_add=True)
    categoria = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.nome}"

class Projeto(models.Model):
    grupo = models.ForeignKey("Grupo", on_delete=models.CASCADE, related_name="grupo_projeto")
    responsavel = models.ForeignKey("User", on_delete=models.CASCADE, related_name="responsavel_projeto")
    membros = models.ManyToManyField("User", blank=True, related_name="membros_projeto")
    nome = models.CharField(max_length=50)
    descricao = models.TextField(max_length=500, blank=True, null=True)
    dia_inicio = models.DateTimeField()
    dia_fim = models.DateTimeField(blank=True, null=True)
    criado = models.DateTimeField(auto_now_add=True)
    categoria = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.nome}"

class Reuniao(models.Model):
    tipo = models.CharField(max_length=20, choices=REUNIOES)
    grupo = models.ForeignKey("Grupo", on_delete=models.CASCADE, related_name="grupo_reuniao", default=None, blank=True, null=True)
    area = models.ForeignKey("Area", on_delete=models.CASCADE, related_name="area_reuniao", default=None, blank=True, null=True)
    dia = models.DateTimeField(auto_now_add=True)
    duracao = models.IntegerField(default=0)
    relatorio = models.FileField(upload_to="relatorios/", blank=True, null=True)

    def __str__(self):
        if self.grupo:
            return f"{self.grupo.nome} - {self.dia}"
        if self.area:
            return f"{self.area.nome} - {self.dia}"
        else:
            return f"{self.tipo} - {self.dia}"

class Presenca(models.Model):
    reuniao = models.ForeignKey(Reuniao, on_delete=models.CASCADE, null=True, blank=True)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, null=True, blank=True)
    membro = models.ForeignKey("User", on_delete=models.CASCADE)
    status_presenca = models.FloatField(choices=PRESENCA)

    def __str__(self):
        if self.reuniao:
            return f"{self.reuniao} - {self.membro}"
        if self.evento:
            return f"{self.evento} - {self.membro}"
        else:
            return f"{self.membro}"


class Links(models.Model):
    grupo = models.ForeignKey("Grupo", on_delete=models.CASCADE, related_name="links_grupo", default=None, blank=True, null=True)
    area = models.ForeignKey("Area", on_delete=models.CASCADE, related_name="links_area", default=None, blank=True, null=True)
    nome = models.CharField(max_length=50)
    link = models.URLField()

    def __str__(self):
        return f"{self.nome}"