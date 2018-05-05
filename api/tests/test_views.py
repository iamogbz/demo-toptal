"""
Test api endpoints
"""
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Account
from api.tests import AccountMixin
from api.utils import peek


class AccountViewsTest(AccountMixin, APITestCase):
    """
    Test api account views
    """

    def test_no_auth_access_denied(self):
        """
        Test access without authentication is denied
        """
        url = reverse('scope-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_auth_access_allowed(self):
        """
        Test authenticated access is allowed
        """
        url = reverse('scope-list')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_super_restricted_route(self):
        """
        Test superusers only route
        """
        url = reverse('auth-list')
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_account_create(self):
        """
        Test user sign up
        """
        url = reverse('account-list')
        test_email = 'randomuser@example.com'
        data = {
            'username': test_email,
            'email': test_email,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(Account.objects.filter(email=test_email).first())

    def test_account_signin_status(self):
        """
        Test user sign in
        """
        url = reverse('auth-user')
        test_pass = get_random_string(16)
        self.user.set_password(test_pass)
        self.user.save()
        data = {
            'email': self.user.email,
            'password': 'invalid-password',
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data['password'] = test_pass
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_account_password_reset(self):
        """
        Test account password reset request
        """
        url = reverse('auth-reset')
        acc = self.user
        acc.clear_reset_code(True)
        self.assertIsNone(acc.reset_code)
        data = {'email': acc.email}
        response = self.client.get(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        acc.refresh_from_db()
        self.assertIsNotNone(acc.reset_code)

    def test_account_reset_confirm(self):
        """
        Test account password reset confirm
        """
        url = reverse('auth-reset')
        acc = self.user
        reset_code = get_random_string(16)
        acc.set_reset_code(reset_code, True)
        data = {
            'email': acc.email,
            'code': 'invalid-reset-code',
            'password': get_random_string(16),
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data['code'] = reset_code
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        acc.refresh_from_db()
        self.assertIsNone(acc.reset_code)
        self.assertTrue(acc.check_password(data['password']))

    def test_account_read(self):
        """
        Test read access to user account
        """
        acc = self.user
        self.client.force_authenticate(acc)
        url = reverse('account-detail', args=[self.mgr.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        url = reverse('account-profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_account_update(self):
        """
        Test updating of user account
        """
        test_email = 'testaccount@example.com'
        acc = Account.objects.create(
            username=test_email,
            email=test_email,
        )
        self.client.force_authenticate(acc)
        data = {'email': 'test-email@example.com'}
        url = reverse('account-detail', args=[self.user.id])
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        url = reverse('account-profile')
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        acc.refresh_from_db()
        self.assertEqual(acc.email, data['email'])

    def test_account_delete(self):
        """
        Test deletion of user account
        """
        acc = self.user
        self.client.force_authenticate(acc)
        url = reverse('account-detail', args=[self.mgr.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        url = reverse('account-profile')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist):
            acc.refresh_from_db()

    def test_account_superuser_rud(self):
        """
        Test superuser has access to RUD operations on any account
        """
        self.client.force_authenticate(self.superuser)
        url = reverse('account-detail', args=[3])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(
            url, data={'email': 'test-email@example.com'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class TripViewsTest(AccountMixin, APITestCase):
    """
    Test api trip views
    """

    def test_user_trips_create(self):
        """
        Test create user trip
        """
        url = reverse('trip-list')
        data = {
            'length_distance': 200,
            'length_time': 1200,
        }
        self.client.force_authenticate(self.user)
        response = self.client.post(url, data=data)
        self.assertContains(
            response, 'date_created',
            status_code=status.HTTP_201_CREATED,
        )

    def test_user_trips_create_invalid(self):
        """
        Test cannot create trip with invalid values
        """
        url = reverse('trip-list')
        self.client.force_authenticate(self.user)
        data = {
            'length_time': -2000,
            'length_distance': 40,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = {
            'length_time': 2000,
            'length_distance': -40,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_trips_read(self):
        """
        Test access on /account/1/trips and /trips
        """
        self.client.force_authenticate(self.user)
        url = reverse('trip-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'count')
        url = reverse('account-trips', args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'count')

    def test_user_trips_update(self):
        """
        Test update on account trips
        """
        new_length_distance = 23
        trip = self.user.trips.first()
        self.assertNotEqual(trip.length_distance, new_length_distance)
        url = reverse('trip-detail', args=[trip.id])
        self.client.force_authenticate(self.user)
        response = self.client.patch(url, data={
            'length_distance': new_length_distance,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        trip.refresh_from_db()
        self.assertEqual(trip.length_distance, new_length_distance)

    def test_user_trips_delete(self):
        """
        Test removal of trip from account
        """
        trip = self.user.trips.first()
        url = reverse('trip-detail', args=[trip.id])
        self.client.force_authenticate(self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist):
            trip.refresh_from_db()

    def test_acc_trips_restricted_crud(self):
        """
        Test create, read, update, delete is restricted for other accounts
        """
        self.client.force_authenticate(self.user)
        url = reverse('account-trips', args=[self.mgr.id])
        data = {
            'length_distance': 100,
            'length_time': 1000,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        trip = self.mgr.trips.first()
        url = reverse('trip-detail', args=[trip.id])
        response = self.client.patch(url, data={
            'length_distance': 32,
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_acc_trips_superuser_crud(self):
        """
        Test create, read, update, delete is allowed for superuser
        """
        self.client.force_authenticate(self.superuser)
        url = reverse('account-trips', args=[self.mgr.id])
        data = {
            'length_distance': 100,
            'length_time': 1000,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        trip = self.mgr.trips.first()
        url = reverse('trip-detail', args=[trip.id])
        response = self.client.patch(url, data={
            'length_distance': 32,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist):
            trip.refresh_from_db()


class AccountManagerTest(AccountMixin, APITestCase):
    """
    Test account manager endpoints
    """

    def test_acc_manager_authorise(self):
        """
        Test user account request for manager
        """
        url = reverse('account-managers')
        self.client.force_authenticate(self.mgr)
        data = {'email': self.user.email}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        auth = Account.get_manage_scope().auths.filter(
            user_id=self.mgr.id, owner_id=self.user.id,
        ).exclude(code__isnull=True, code__exact='').last()
        self.assertIsNotNone(auth)
        self.assertFalse(auth.active)

        url = reverse('account-managing')
        self.client.force_authenticate(self.user)
        dummy_auth_code = 'dumnmy-auth-code'
        data = {'code': dummy_auth_code}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        auth.code = dummy_auth_code
        auth.save()
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        auth.refresh_from_db()
        self.assertIsNone(auth.code)
        self.assertTrue(auth.active)

    def test_get_account_managing(self):
        """
        Test get account managing endpoint
        """
        url = reverse('account-managing')
        self.client.force_authenticate(self.mgr)
        response = self.client.get(url)
        self.assertContains(
            response, 'testuser', status_code=status.HTTP_200_OK)

    def test_get_account_managers(self):
        """
        Test get account managers endpoint
        """
        url = reverse('account-managers')
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        self.assertContains(
            response, 'testmanager', status_code=status.HTTP_200_OK)

    def test_acc_manager_trip_create(self):
        """
        Test account manager create trip
        """
        url = reverse('account-trips', args=[peek(self.mgr.managing)])
        data = {
            'length_distance': 200,
            'length_time': 1200,
        }
        self.client.force_authenticate(self.mgr)
        response = self.client.post(url, data=data)
        self.assertContains(
            response, 'date_created',
            status_code=status.HTTP_201_CREATED,
        )

    def test_acc_manager_trip_retrieve(self):
        """
        Test manager access to user trips
        """
        self.client.force_authenticate(self.mgr)
        url = reverse('account-trips', args=[peek(self.mgr.managing)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'count')

    def test_acc_manager_trip_update(self):
        """
        Test manager access to update trip
        """
        new_length_distance = 23
        trip = self.user.trips.first()
        self.assertNotEqual(trip.length_distance, new_length_distance)
        url = reverse('trip-detail', args=[trip.id])
        self.client.force_authenticate(self.mgr)
        response = self.client.patch(url, data={
            'length_distance': new_length_distance,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        trip.refresh_from_db()
        self.assertEqual(trip.length_distance, new_length_distance)

    def test_acc_manager_trip_delete(self):
        """
        Test manager access to delete trip
        """
        trip = self.user.trips.first()
        url = reverse('trip-detail', args=[trip.id])
        self.client.force_authenticate(self.mgr)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist):
            trip.refresh_from_db()

    def test_acc_manager_deauthorise(self):
        """
        Test deauthorisation of manager
        """
        url = reverse('account-managers')
        self.client.force_authenticate(self.user)
        data = {'email': self.mgr.email}
        response = self.client.delete(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertNotIn(self.mgr.id, self.user.managers)
