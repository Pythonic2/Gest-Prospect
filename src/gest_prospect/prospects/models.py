import re
from string import Formatter
from urllib.parse import quote

from django.core.exceptions import ValidationError
from django.db import models


DEFAULT_WHATSAPP_MESSAGE = """Olá, {nome_empresa},
tudo bem? Sou Igor, da GEST TECH MARINHO, aqui de João Pessoa. Trabalho ajudando empresas a reduzir tarefas manuais e melhorar processos através de automações, integrações e sistemas sob medida.
Estou conversando com alguns escritórios contábeis da região e queria te fazer uma pergunta rápida: hoje vocês têm alguma rotina repetitiva que toma bastante tempo da equipe?"""


class MessageTemplate(models.Model):
    name = models.CharField("nome", max_length=120)
    body = models.TextField("mensagem", help_text="Use {nome_empresa} para inserir o nome do prospect.")
    is_active = models.BooleanField("ativo", default=True)
    is_default = models.BooleanField("padrão", default=False)
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        ordering = ["-is_default", "name"]
        verbose_name = "modelo de mensagem"
        verbose_name_plural = "modelos de mensagem"

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        super().clean()
        try:
            fields = {field_name for _, field_name, _, _ in Formatter().parse(self.body) if field_name}
        except ValueError as error:
            raise ValidationError({"body": "As chaves da mensagem estão incompletas."}) from error
        unsupported_fields = fields - {"nome_empresa"}
        if unsupported_fields:
            raise ValidationError({"body": "Use somente a variável {nome_empresa}."})

    def save(self, *args, **kwargs):
        if self.is_default:
            type(self).objects.exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def render_for(self, company_name: str) -> str:
        return self.body.format(nome_empresa=company_name)


class Segment(models.Model):
    name = models.CharField("segmento", max_length=120, unique=True)
    created_at = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "segmento"
        verbose_name_plural = "segmentos"

    def __str__(self) -> str:
        return self.name


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
    segment = models.ForeignKey(
        Segment,
        verbose_name="segmento",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prospects",
    )
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
        return self.get_whatsapp_url()

    def get_whatsapp_url(self, message_template: MessageTemplate | None = None) -> str:
        if not self.whatsapp_number:
            return ""
        message = (
            message_template.render_for(self.name)
            if message_template
            else DEFAULT_WHATSAPP_MESSAGE.format(nome_empresa=self.name)
        )
        return f"https://wa.me/{self.whatsapp_number}?text={quote(message)}"
