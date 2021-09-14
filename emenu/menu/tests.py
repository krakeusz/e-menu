from datetime import date, timedelta
from emenu.menu.models import Dish
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.contrib.auth.models import User
from django.test import TestCase
from emenu.menu.tasks import get_new_dishes_mail_contents
from rest_framework import status
from rest_framework.test import APITestCase
import json
import re


class PublicApiTests(APITestCase):
    fixtures = ['testing.json']

    def test_root_view_contains_link_to_documentation(self):
        url = reverse('root')
        response = self.client.get(url)
        self.assertContains(response, '/docs/', status_code=status.HTTP_200_OK)

    def test_swagger_documentation_is_visible_to_public(self):
        url = reverse('swagger-ui')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fetching_list_of_menus(self):
        url = reverse('public-menu-list')
        response = self.client.get(url, format='json')
        self.assertContains(response, 'September Menu',
                            status_code=status.HTTP_200_OK)
        self.assertContains(response, 'August Menu')
        self.assertContains(response, 'October Menu')

        # empty menus should be invisible
        self.assertNotContains(response, "November Menu")

    def test_fetching_single_menu(self):
        url = reverse('public-menu-detail', kwargs={'pk': 1})
        response = self.client.get(url, format='json')
        self.assertContains(
            response, 'The famous potato wedges deep fried in fresh oil.', status_code=status.HTTP_200_OK)
        self.assertNotContains(response, "Tap water")

    def __assert_before(self, string1, string2, response):
        """
        Assert that needle1 appears before needle2 in haystack. Both need to appear.
        """
        self.assertIsNotNone(
            re.search(f'{string1}.*{string2}', str(response.content)), f'{string1} is not before {string2} in the response')

    def test_ordering_menus(self):
        url = reverse('public-menu-list') + '?ordering=-dishes__count,name'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # October Menu has 5 dishes, more than any other
        self.__assert_before('October Menu', 'August Menu', response)
        # 'August' is before 'September' in dictionary
        self.__assert_before('August Menu', 'September Menu', response)

    def test_filtering_menu_exact_name(self):
        url = reverse('public-menu-list') + '?name=October+Menu'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_response = json.loads(response.content)
        self.assertEqual(len(json_response), 1)
        self.assertEqual(json_response[0]['name'], 'October Menu')

    def test_filtering_menu_nonexistent_name(self):
        url = reverse('public-menu-list') + '?name=nonexistentmenu'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_response = json.loads(response.content)
        self.assertEqual(len(json_response), 0)

    def test_filtering_menu_date_added(self):
        url = reverse('public-menu-list') + \
            '?date_added__lt=2021-09-13&date_added__gte=2021-09-12'
        response = self.client.get(url, format='json')
        json_response = json.loads(response.content)
        self.assertEqual(len(json_response), 2)


class PrivateApiTests(APITestCase):
    fixtures = ['testing.json']

    def __authenticate(self):
        User.objects.create_user(username='Eve', password='abc')
        self.assertTrue(self.client.login(username='Eve', password='abc'))

    def test_dish_api_inaccessible_to_public(self):
        url = reverse('dish-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_fetching_all_dishes(self):
        url = reverse('dish-list')
        self.__authenticate()
        response = self.client.get(url, format='json')
        json_response = json.loads(response.content)
        self.assertContains(
            response, 'The fresh salad with Greek feta cheese.', status_code=status.HTTP_200_OK)
        self.assertEqual(len(json_response), 6)

    def test_posting_new_dish(self):
        url = reverse('dish-list')
        self.__authenticate()
        response = self.client.post(url, format='json', data={
            'name': 'Risotto',
            'description': 'A dish made of slowly cooked rice.',
            'price': 9.90,
            'preparation_time': '00:35:00',
            'is_vegan': True
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # make sure that the dish has really been created
        url = reverse('dish-list')
        response = self.client.get(url, format='json')
        self.assertContains(response, 'Risotto',
                            status_code=status.HTTP_200_OK)

    def test_deleting_dish(self):
        url = reverse('dish-detail', kwargs={'pk': 1})
        self.__authenticate()
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # make sure that the dish has really been deleted
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_menu_api_inaccessible_to_public(self):
        url = reverse('private-menu-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_changing_menu(self):
        url = reverse('private-menu-detail', kwargs={'pk': 3})
        self.__authenticate()
        response = self.client.patch(url, format='json', data={
                                     'name': 'OctoberFEST Menu'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(url, format='json')
        self.assertContains(response, 'OctoberFEST Menu',
                            status_code=status.HTTP_200_OK)
        response_dict = json.loads(response.content)
        date_modified = response_dict['date_modified']
        self.assertGreater(parse_datetime(date_modified), timezone.now() -
                           timedelta(minutes=1))

    def test_cannot_add_duplicate_menu_name(self):
        url = reverse('private-menu-list')
        self.__authenticate()
        response = self.client.post(url, format='json', data={
            'name': 'September Menu',
            'description': 'Another menu for September',
            'dishes': []
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_add_new_menu(self):
        url = reverse('private-menu-list')
        self.__authenticate()
        response = self.client.post(url, format='json', data={
            'name': 'Another September Menu',
            'description': 'Another menu for September',
            'dishes': []
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify that menu has been added with the current date.
        response_dict = json.loads(response.content)
        self.assertGreater(parse_datetime(response_dict['date_modified']), timezone.now() -
                           timedelta(minutes=1))


class ReportTests(TestCase):
    fixtures = ['testing.json']

    def test_new_dishes_email_content(self):
        french_fries = Dish.objects.filter(pk=1).get()
        yesterday = date.today() - timedelta(days=1)
        french_fries.date_added = yesterday
        french_fries.save()
        User.objects.create_user(
            username='Eve', password='abc', email='eve@example.com')

        results = get_new_dishes_mail_contents()

        self.assertEqual(len(results), 1)
        email_content = results[0][1]
        self.assertGreater(email_content.find('Eve'), -1)
        self.assertGreater(email_content.find('New recipes'), -1)
        self.assertGreater(email_content.find('French fries'), -1)
