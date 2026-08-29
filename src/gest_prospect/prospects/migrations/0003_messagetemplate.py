from django.db import migrations, models


DEFAULT_MESSAGE = """Olá, {nome_empresa},
tudo bem? Sou Igor, da GEST TECH MARINHO, aqui de João Pessoa. Trabalho ajudando empresas a reduzir tarefas manuais e melhorar processos através de automações, integrações e sistemas sob medida.
Estou conversando com alguns escritórios contábeis da região e queria te fazer uma pergunta rápida: hoje vocês têm alguma rotina repetitiva que toma bastante tempo da equipe?"""


def create_default_template(apps, schema_editor):
    MessageTemplate = apps.get_model("prospects", "MessageTemplate")
    MessageTemplate.objects.create(
        name="Abordagem inicial — escritórios contábeis",
        body=DEFAULT_MESSAGE,
        is_active=True,
        is_default=True,
    )


class Migration(migrations.Migration):
    dependencies = [("prospects", "0002_prospect_contacted_at")]

    operations = [
        migrations.CreateModel(
            name="MessageTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, verbose_name="nome")),
                ("body", models.TextField(help_text="Use {nome_empresa} para inserir o nome do prospect.", verbose_name="mensagem")),
                ("is_active", models.BooleanField(default=True, verbose_name="ativo")),
                ("is_default", models.BooleanField(default=False, verbose_name="padrão")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="criado em")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="atualizado em")),
            ],
            options={
                "verbose_name": "modelo de mensagem",
                "verbose_name_plural": "modelos de mensagem",
                "ordering": ["-is_default", "name"],
            },
        ),
        migrations.RunPython(create_default_template, migrations.RunPython.noop),
    ]
