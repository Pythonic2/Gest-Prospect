from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Prospect


class ProspectModelTests(TestCase):
    def test_whatsapp_url_uses_brazilian_country_code_and_company_name(self):
        prospect = Prospect(name="Contábil & Cia", phone="(83) 99999-1234")

        parsed_url = urlparse(prospect.whatsapp_url)

        self.assertEqual(parsed_url.netloc, "wa.me")
        self.assertEqual(parsed_url.path, "/5583999991234")
        self.assertIn("Olá, Contábil & Cia, tudo bem?", parse_qs(parsed_url.query)["text"][0])

    def test_whatsapp_url_is_empty_without_phone(self):
        prospect = Prospect(name="Sem telefone", phone="")

        self.assertEqual(prospect.whatsapp_url, "")


class ImportProspectsCommandTests(TestCase):
    @patch("gest_prospect.prospects.management.commands.import_prospects.search_places")
    def test_import_creates_and_then_updates_same_place(self, search_places):
        search_places.return_value = [{
            "id": "place-123",
            "displayName": {"text": "Empresa Teste"},
            "formattedAddress": "João Pessoa, PB",
            "nationalPhoneNumber": "(83) 3333-4444",
            "rating": 4.5,
            "userRatingCount": 10,
        }]

        with patch.dict("os.environ", {"GOOGLE_MAPS_API_KEY": "test-key"}):
            call_command("import_prospects", limit=1)
            search_places.return_value[0]["userRatingCount"] = 11
            call_command("import_prospects", limit=1)

        self.assertEqual(Prospect.objects.count(), 1)
        self.assertEqual(Prospect.objects.get().user_rating_count, 11)
        search_places.assert_called_with("escritório de contabilidade João Pessoa", "test-key", 60)

    @patch("gest_prospect.prospects.management.commands.import_prospects.search_places")
    def test_import_skips_existing_place_and_creates_next_one(self, search_places):
        Prospect.objects.create(place_id="existing", name="Já cadastrado")
        search_places.return_value = [
            {"id": "existing", "displayName": {"text": "Atualizado"}},
            {"id": "new-place", "displayName": {"text": "Empresa Nova"}},
        ]

        with patch.dict("os.environ", {"GOOGLE_MAPS_API_KEY": "test-key"}):
            call_command("import_prospects", limit=1)

        self.assertEqual(Prospect.objects.count(), 2)
        self.assertTrue(Prospect.objects.filter(place_id="new-place").exists())


class ProspectViewsTests(TestCase):
    def setUp(self):
        self.prospect = Prospect.objects.create(
            place_id="place-view",
            name="Empresa da Interface",
            phone="(83) 99999-1234",
            website_url="https://empresa.example.com",
        )

    def test_list_displays_prospect(self):
        response = self.client.get(reverse("prospects:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Empresa da Interface")
        self.assertContains(response, "Enviar WhatsApp")
        self.assertContains(response, "https://empresa.example.com")

    def test_open_whatsapp_marks_prospect_as_contacted(self):
        response = self.client.post(reverse("prospects:open_whatsapp", args=[self.prospect.pk]))

        self.prospect.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("https://wa.me/5583999991234"))
        self.assertEqual(self.prospect.status, Prospect.Status.CONTACTED)
        self.assertIsNotNone(self.prospect.contacted_at)

    def test_status_can_be_changed_from_interface(self):
        response = self.client.post(
            reverse("prospects:update_status", args=[self.prospect.pk]),
            {"status": Prospect.Status.INTERESTED},
        )

        self.prospect.refresh_from_db()
        self.assertRedirects(response, reverse("prospects:list"))
        self.assertEqual(self.prospect.status, Prospect.Status.INTERESTED)
