import argparse
import os
import sys
from dotenv import load_dotenv
import requests
load_dotenv()

PLACES_TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
DEFAULT_QUERY = "escritório de contabilidade João Pessoa"
FIELDS = (
    "nextPageToken,"
    "places.id,"
    "places.displayName,"
    "places.formattedAddress,"
    "places.nationalPhoneNumber,"
    "places.websiteUri,"
    "places.rating,"
    "places.userRatingCount,"
    "places.googleMapsUri"
)


def search_places(query: str, api_key: str, limit: int = 30) -> list[dict]:
    if not 1 <= limit <= 60:
        raise ValueError("O limite deve estar entre 1 e 60.")

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": FIELDS,
    }
    places = []
    page_token = None

    while len(places) < limit:
        body = {
            "textQuery": query,
            "languageCode": "pt-BR",
            "regionCode": "BR",
            "pageSize": min(20, limit - len(places)),
        }
        if page_token:
            body["pageToken"] = page_token

        response = requests.post(
            PLACES_TEXT_SEARCH_URL,
            headers=headers,
            json=body,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        places.extend(data.get("places", []))
        page_token = data.get("nextPageToken")

        if not page_token:
            break

    return places[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(description="Busca textual na Google Places API")
    parser.add_argument("query", nargs="?", default=DEFAULT_QUERY)
    parser.add_argument(
        "--limit",
        type=int,
        choices=range(1, 61),
        default=30,
        metavar="1-60",
        help="quantidade máxima de resultados (padrão: 30)",
    )
    args = parser.parse_args()

    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        sys.exit("Defina a variável de ambiente GOOGLE_MAPS_API_KEY.")

    try:
        places = search_places(args.query, api_key, args.limit)
    except requests.HTTPError as error:
        detail = error.response.text if error.response is not None else str(error)
        sys.exit(f"Erro da Google Places API: {detail}")
    except requests.RequestException as error:
        sys.exit(f"Erro ao realizar a requisição: {error}")

    if not places:
        print("Nenhum local encontrado.")
        return

    for index, place in enumerate(places, start=1):
        print(f"\n{index}. {place.get('displayName', {}).get('text', 'Sem nome')}")
        print(f"   Endereço: {place.get('formattedAddress', 'Não informado')}")
        print(f"   Telefone: {place.get('nationalPhoneNumber', 'Não informado')}")
        print(f"   Avaliação: {place.get('rating', 'Não informada')} "
              f"({place.get('userRatingCount', 0)} avaliações)")
        print(f"   Site: {place.get('websiteUri', 'Não informado')}")
        print(f"   Google Maps: {place.get('googleMapsUri', 'Não informado')}")

if __name__ == "__main__":
    main()
