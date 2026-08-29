# Gest Prospect

Cadastro de prospects com Django e consulta à Google Places API.

## Preparar o banco

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py createsuperuser
```

## Importar prospects

Ative a **Places API (New)** no Google Cloud, crie uma chave de API e execute:

```bash
cp .env.example .env
# Preencha GOOGLE_MAPS_API_KEY no arquivo .env
uv run python manage.py import_prospects --limit 30
```

A busca padrão é `escritorio de contabilidade em joao pessoa`. Para usar outro
termo, passe-o como argumento:

```bash
uv run python manage.py import_prospects "clinicas odontologicas em joao pessoa" --limit 40
```

O `--limit` define quantos prospects **novos** devem ser cadastrados. O comando
consulta até 60 candidatos, pula os que já existem e continua até atingir esse
limite. Cada página contém no máximo 20 resultados e representa uma requisição
separada à API.

O `place_id` impede duplicações. Os registros encontrados novamente são
atualizados sem perder o status de contato. Como uma busca textual do Google
disponibiliza no máximo 60 resultados, depois de esgotá-los é necessário variar
o termo ou a localização da busca para encontrar novos prospects.

## Abrir o admin

```bash
uv run python manage.py runserver
```

Acesse `http://127.0.0.1:8000/` para usar a interface de prospecção. Nela é
possível importar, pesquisar, filtrar, alterar o status e abrir a mensagem no
WhatsApp. Ao abrir o WhatsApp, o prospect é marcado como contatado e a data fica
registrada para evitar contatos repetidos.

O painel administrativo continua disponível em `http://127.0.0.1:8000/admin/`.
