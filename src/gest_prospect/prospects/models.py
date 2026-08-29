import re
from urllib.parse import quote

from django.db import models


WHATSAPP_MESSAGE = """Olá, {nome_empresa}, tudo bem? Meu nome é Igor, sou da GEST TECH MARINHO aqui de João Pessoa. Trabalhamos com automação de processos para empresas e estou entrando em contato com alguns escritórios contábeis da região.

Queria fazer uma pergunta rápida: vocês têm alguma rotina que a equipe ainda faz manualmente todos os dias, como baixar documentos em portais, atualizar planilhas, conferir informações, gerar relatórios ou passar dados de um sistema para outro?

Dependendo do processo, conseguimos automatizar boa parte desse trabalho. Se fizer sentido, posso avaliar um processo de vocês sem compromisso."""


class Prospect(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Novo"
        CONTACTED = "contacted", "Contatado"
        INTERESTED = "interested", "Interessado"
        NOT_INTERESTED = "not_interested", "Sem interesse"

    place_id = models.CharField("ID do Google Places", max_length=255, unique=True)
    name = models.CharField("empresa", max_length=255)
    address = models.CharField("endereço", max_length=500, blank=True)
    phone = models.CharField("telefone", max_length=50, blank=True)
    website_url = models.URLField("site", max_length=1000, blank=True)
    google_maps_url = models.URLField("Google Maps", max_length=1000, blank=True)
    rating = models.DecimalField("avaliação", max_digits=2, decimal_places=1, null=True, blank=True)
    user_rating_count = models.PositiveIntegerField("quantidade de avaliações", default=0)
    source_query = models.CharField("termo pesquisado", max_length=500, blank=True)
    status = models.CharField("status", max_length=20, choices=Status.choices, default=Status.NEW)
    contacted_at = models.DateTimeField("contatado em", null=True, blank=True)
    created_at = models.DateTimeField("cadastrado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "prospect"
        verbose_name_plural = "prospects"

    def __str__(self) -> str:
        return self.name

    @property
    def whatsapp_number(self) -> str:
        number = re.sub(r"\D", "", self.phone)
        if 10 <= len(number) <= 11:
            number = f"55{number}"
        return number

    @property
    def whatsapp_url(self) -> str:
        if not self.whatsapp_number:
            return ""
        message = WHATSAPP_MESSAGE.format(nome_empresa=self.name)
        return f"https://wa.me/{self.whatsapp_number}?text={quote(message)}"
