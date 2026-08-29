import os

import requests
from django.core.management.base import BaseCommand, CommandError

from gest_prospect.main import DEFAULT_QUERY, search_places
from gest_prospect.prospects.models import Prospect


class Command(BaseCommand):
    help = "Busca empresas no Google Places e cadastra apenas prospects novos"

    def add_arguments(self, parser):
        parser.add_argument("query", nargs="?", default=DEFAULT_QUERY)
        parser.add_argument(
            "--limit",
            type=int,
            choices=range(1, 61),
            default=30,
            help="quantidade desejada de novos prospects (padrão: 30)",
        )

    def handle(self, *args, **options):
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not api_key:
            raise CommandError("Defina GOOGLE_MAPS_API_KEY no ambiente ou no arquivo .env.")

        query = options["query"]
        new_prospects_limit = options["limit"]
        try:
            # A busca textual disponibiliza no máximo 60 candidatos. Consultamos
            # todos para conseguir avançar além dos já cadastrados.
            places = search_places(query, api_key, 60)
        except requests.RequestException as error:
            detail = error.response.text if error.response is not None else str(error)
            raise CommandError(f"Erro da Google Places API: {detail}") from error

        created_count = 0
        updated_count = 0
        for place in places:
            if created_count >= new_prospects_limit:
                break

            _, created = Prospect.objects.update_or_create(
                place_id=place["id"],
                defaults={
                    "name": place.get("displayName", {}).get("text", "Sem nome"),
                    "address": place.get("formattedAddress", ""),
                    "phone": place.get("nationalPhoneNumber", ""),
                    "website_url": place.get("websiteUri", ""),
                    "google_maps_url": place.get("googleMapsUri", ""),
                    "rating": place.get("rating"),
                    "user_rating_count": place.get("userRatingCount", 0),
                    "source_query": query,
                },
            )
            created_count += int(created)
            updated_count += int(not created)

        self.stdout.write(self.style.SUCCESS(
            f"Importação concluída: {created_count} novos e {updated_count} existentes atualizados."
        ))
        if created_count < new_prospects_limit:
            self.stdout.write(self.style.WARNING(
                "A busca não forneceu novos resultados suficientes. "
                "Tente outro termo ou uma localização mais específica."
            ))
