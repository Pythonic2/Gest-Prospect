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

## Docker

Os arquivos usam a porta `8003` por padrão. Prepare o ambiente e suba o serviço:

```bash
cp .env.example .env
# Preencha GOOGLE_MAPS_API_KEY e DJANGO_SECRET_KEY
docker compose up --build -d
```

No Portainer, carregue as variáveis na seção **Environment variables**. Não é
necessário enviar ou montar um arquivo `.env`: o Compose repassa explicitamente
essas variáveis ao container.

A aplicação ficará disponível em `http://localhost:8003/`. O SQLite é persistido
no volume nomeado `django_data`, e as migrations são aplicadas na inicialização.

Em produção, configure pelo menos:

```dotenv
DJANGO_DEBUG=false
DJANGO_SECRET_KEY=uma-chave-longa-aleatoria
APP_PORT=8003
APP_URL=https://prospects.seudominio.com.br
DJANGO_ALLOWED_HOSTS=prospects.seudominio.com.br
DJANGO_CSRF_TRUSTED_ORIGINS=https://prospects.seudominio.com.br
DJANGO_SECURE_SSL_REDIRECT=true
DATABASE_PATH=/app/data/db.sqlite3
```

Para usar PostgreSQL no Neon, configure também:

```dotenv
DB_NAME=neondb
DB_USER=neondb_owner
DB_PASSWORD=sua-senha
DB_HOST=seu-endpoint.sa-east-1.aws.neon.tech
DB_PORT=5432
DB_SCHEMA=
DB_SSLMODE=require
DB_CHANNEL_BINDING=require
DB_CONNECT_TIMEOUT=10
DB_CONN_MAX_AGE=60
```

Quando `DB_HOST` estiver vazio, o projeto usa SQLite. Quando estiver preenchido,
o Django seleciona PostgreSQL automaticamente.

Para recriar os arquivos Docker ou escolher outra porta:

```bash
uv run python scripts/generate_docker.py --port 8003
```

O gerador aceita também `--project`, `--module` e `--output`.
