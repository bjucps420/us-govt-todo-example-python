import mock
from django.contrib.auth.models import User
from django.test import Client, TestCase
from json import dumps, loads


class AuthTestCases(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='temporary',
            email='temporary@gmail.com',
            password='temporary')

    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.retrieve_user_by_email',
                return_value=mock.Mock(was_successful=lambda: False, status=400))
    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.register',
                return_value=mock.Mock(was_successful=lambda: True, status=200,
                                       success_response={"user":{"id":"a718745d-e6bc-45d7-aaec-1ca45d417bb4"}}))
    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.retrieve_registration',
                return_value=mock.Mock(was_successful=lambda: True, status=200,
                                       success_response={"registration":{"roles":[]}}))
    def test_register_success(self, mock1, mock2, mock3):
        c = Client()
        response = c.post(
            '/api/auth/register',
            dumps({"name": "test", "password": "test", "username": "test"}),
            content_type="application/json"
        )
        body = loads(response.content)
        self.assertLess(response.status_code, 300)
        self.assertEqual(body["success"], True)

    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.retrieve_user_by_email',
                return_value=mock.Mock(was_successful=lambda: True, status=200,
                                       success_response={"user":{"id":"a718745d-e6bc-45d7-aaec-1ca45d417bb4"}}))
    def test_register_preexisting_account(self, mock1):
        c = Client()
        response = c.post(
            '/api/auth/register',
            dumps({"name": "test", "password": "test", "username": "test"}),
            content_type="application/json"
        )
        body = loads(response.content)
        self.assertLess(response.status_code, 300)
        self.assertEqual(body["success"], False)

    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.retrieve_user_by_login_id',
                return_value=mock.Mock(was_successful=lambda: True, status=200,
                                       success_response={"user":{"id":"a718745d-e6bc-45d7-aaec-1ca45d417bb4"}}))
    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.forgot_password',
                return_value=mock.Mock(was_successful=lambda: True, status=200))
    def test_forgot_password_success(self, mock1, mock2):
        c = Client()
        response = c.get(
            '/api/auth/forgot-password?user=test',
        )
        body = loads(response.content)
        self.assertLess(response.status_code, 300)
        self.assertEqual(body["success"], True)

    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.retrieve_user_by_login_id',
                return_value=mock.Mock(was_successful=lambda: False, status=400))
    def test_forgot_password_failure(self, mock1):
        c = Client()
        response = c.get(
            '/api/auth/forgot-password?user=test',
        )
        body = loads(response.content)
        self.assertLess(response.status_code, 300)
        self.assertEqual(body["success"], True)

    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.login',
                return_value=mock.Mock(was_successful=lambda: True, status=200,
                                       success_response={"id":"a718745d-e6bc-45d7-aaec-1ca45d417bb4"}))
    def test_login_success(self, mock1):
        c = Client()
        response = c.post(
            '/api/auth/login',
            dumps({"username": "test", "password": "test"}),
            content_type="application/json"
        )
        body = loads(response.content)
        self.assertLess(response.status_code, 300)
        self.assertEqual(body["success"], True)
        self.assertEqual(body["response"]["success"], True)

    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.login',
                return_value=mock.Mock(was_successful=lambda: False, status=401))
    def test_login_failure(self, mock1):
        c = Client()
        response = c.post(
            '/api/auth/login',
            dumps({"username": "test", "password": "test"}),
            content_type="application/json"
        )
        body = loads(response.content)
        self.assertLess(response.status_code, 300)
        self.assertEqual(body["success"], True)
        self.assertEqual(body["response"]["success"], False)

    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.login',
                return_value=mock.Mock(was_successful=lambda: False, status=401))
    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.retrieve_user_by_change_password_id',
                return_value=mock.Mock(was_successful=lambda: True, status=200,
                                       success_response={"user":{"id": "a718745d-e6bc-45d7-aaec-1ca45d417bb4"}}))
    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.retrieve_user',
                return_value=mock.Mock(was_successful=lambda: True, status=200,
                                       success_response={"user":{"id": "a718745d-e6bc-45d7-aaec-1ca45d417bb4"}}))
    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.retrieve_user_by_login_id',
                return_value=mock.Mock(was_successful=lambda: True, status=200,
                                       success_response={"user": {"id": "a718745d-e6bc-45d7-aaec-1ca45d417bb4"}}))
    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.update_user',
                return_value=mock.Mock(was_successful=lambda: True, status=200))
    def test_login_forgot_password_success(self, mock1, mock2, mock3, mock4, mock5):
        c = Client()
        response = c.post(
            '/api/auth/login',
            dumps({"username": "test", "password": "test", "forgotPasswordCode": "test", "newPassword": "test"}),
            content_type="application/json"
        )
        body = loads(response.content)
        self.assertLess(response.status_code, 300)
        self.assertEqual(body["success"], True)
        self.assertEqual(body["response"]["success"], True)

    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.login',
                return_value=mock.Mock(was_successful=lambda: True, status=242))
    def test_login_two_factor_required(self, mock1):
        c = Client()
        response = c.post(
            '/api/auth/login',
            dumps({"username": "test", "password": "test", "twoFactorCode": None}),
            content_type="application/json"
        )
        body = loads(response.content)
        self.assertLess(response.status_code, 300)
        self.assertEqual(body["success"], True)
        self.assertEqual(body["response"]["success"], True)

    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.login',
                return_value=mock.Mock(was_successful=lambda: True, status=242,
                                       success_response={"user": {"id": "a718745d-e6bc-45d7-aaec-1ca45d417bb4"}, "twoFactorId": "test"}))
    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.retrieve_user_by_login_id',
                return_value=mock.Mock(was_successful=lambda: True, status=200,
                                       success_response={"user": {"id": "a718745d-e6bc-45d7-aaec-1ca45d417bb4"}}))
    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.two_factor_login',
                return_value=mock.Mock(was_successful=lambda: True, status=200))
    def test_login_two_factor_supplied(self, mock1, mock2, mock3):
        c = Client()
        response = c.post(
            '/api/auth/login',
            dumps({"username": "test", "password": "test", "twoFactorCode": "test"}),
            content_type="application/json"
        )
        body = loads(response.content)
        self.assertLess(response.status_code, 300)
        self.assertEqual(body["success"], True)
        self.assertEqual(body["response"]["success"], True)

    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.login',
                return_value=mock.Mock(was_successful=lambda: True, status=203))
    def test_login_password_change_required(self, mock1):
        c = Client()
        response = c.post(
            '/api/auth/login',
            dumps({"username": "test", "password": "test", "newPassword": None}),
            content_type="application/json"
        )
        body = loads(response.content)
        self.assertLess(response.status_code, 300)
        self.assertEqual(body["success"], True)
        self.assertEqual(body["response"]["success"], True)

    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.login',
                return_value=mock.Mock(was_successful=lambda: True, status=203))
    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.retrieve_user_by_login_id',
                return_value=mock.Mock(was_successful=lambda: True, status=200,
                                       success_response={"user": {"id": "a718745d-e6bc-45d7-aaec-1ca45d417bb4"}}))
    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.retrieve_user',
                return_value=mock.Mock(was_successful=lambda: True, status=200,
                                       success_response={"user": {"id": "a718745d-e6bc-45d7-aaec-1ca45d417bb4"}}))
    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.update_user',
                return_value=mock.Mock(was_successful=lambda: True, status=200))
    def test_login_password_change_supplied(self, mock1, mock2, mock3, mock4):
        c = Client()
        response = c.post(
            '/api/auth/login',
            dumps({"username": "test", "password": "test", "newPassword": "test"}),
            content_type="application/json"
        )
        body = loads(response.content)
        self.assertLess(response.status_code, 300)
        self.assertEqual(body["success"], True)
        self.assertEqual(body["response"]["success"], True)

    @mock.patch('todo.authenticate.FusionAuthBackend.authenticate')
    def test_logout(self, mock1):
        mock1.return_value = self.user
        c = Client()
        logged_in = c.login(username="temporary", password="temporary")
        self.assertEqual(logged_in, True)
        response = c.get(
            '/api/auth/logout',
        )
        body = loads(response.content)
        self.assertLess(response.status_code, 300)
        self.assertEqual(body["success"], True)


class EnumTestCases(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='temporary',
            email='temporary@gmail.com',
            password='temporary')

    @mock.patch('todo.authenticate.FusionAuthBackend.authenticate')
    def test_status(self, mock1):
        mock1.return_value = self.user
        c = Client()
        logged_in = c.login(username="temporary", password="temporary")
        self.assertEqual(logged_in, True)
        response = c.get(
            '/api/enum/status/all',
        )
        body = loads(response.content)
        self.assertLess(response.status_code, 300)
        self.assertEqual(len(body), 3)

    @mock.patch('todo.authenticate.FusionAuthBackend.authenticate')
    def test_type(self, mock1):
        mock1.return_value = self.user
        c = Client()
        logged_in = c.login(username="temporary", password="temporary")
        self.assertEqual(logged_in, True)
        response = c.get(
            '/api/enum/type/all',
        )
        body = loads(response.content)
        self.assertLess(response.status_code, 300)
        self.assertEqual(len(body), 4)


class UserTestCases(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='a718745d-e6bc-45d7-aaec-1ca45d417bb4',
            email='temporary@gmail.com',
            password='temporary')

    def test_current_no_user(self):
        c = Client()
        response = c.get(
            '/api/user/current',
        )
        self.assertLess(response.status_code, 300)
        self.assertNotEquals(response.content, "null")

    @mock.patch('todo.authenticate.FusionAuthBackend.authenticate')
    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.retrieve_user',
                return_value=mock.Mock(was_successful=lambda: True, status=200,
                                       success_response={"user":{"id": "a718745d-e6bc-45d7-aaec-1ca45d417bb4","email":"test","fullName":"test","twoFactor":{"methods":[]}}}))
    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.retrieve_registration',
                return_value=mock.Mock(was_successful=lambda: True, status=200,
                                       success_response={"registration":{"roles":[]}}))
    def test_current_user(self, mock1, mock2, mock3):
        mock3.return_value = self.user
        c = Client()
        logged_in = c.login(username="a718745d-e6bc-45d7-aaec-1ca45d417bb4", password="temporary")
        self.assertEqual(logged_in, True)
        response = c.get(
            '/api/user/current',
        )
        self.assertLess(response.status_code, 300)

    @mock.patch('todo.authenticate.FusionAuthBackend.authenticate')
    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.generate_two_factor_secret',
                return_value=mock.Mock(was_successful=lambda: True, status=200, success_response={}))
    def test_get_secret(self, mock1, mock2):
        mock2.return_value = self.user
        c = Client()
        logged_in = c.login(username="a718745d-e6bc-45d7-aaec-1ca45d417bb4", password="temporary")
        self.assertEqual(logged_in, True)
        response = c.get(
            '/api/user/get-secret',
        )
        body = loads(response.content)
        self.assertLess(response.status_code, 300)
        self.assertEqual(body["success"], True)

    @mock.patch('todo.authenticate.FusionAuthBackend.authenticate')
    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.retrieve_user',
                return_value=mock.Mock(was_successful=lambda: True, status=200,
                                       success_response={"user":{"id":"a718745d-e6bc-45d7-aaec-1ca45d417bb4"}}))
    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.enable_two_factor',
                return_value=mock.Mock(was_successful=lambda: True, status=200, success_response={}))
    def test_toggle_two_factor_on(self, mock1, mock2, mock3):
        mock3.return_value = self.user
        c = Client()
        logged_in = c.login(username="a718745d-e6bc-45d7-aaec-1ca45d417bb4", password="temporary")
        self.assertEqual(logged_in, True)
        response = c.post(
            '/api/user/toggle-two-factor',
            dumps({"enableTwoFactor": True, "code": "test", "secret": "test"}),
            content_type="application/json"
        )
        body = loads(response.content)
        self.assertLess(response.status_code, 300)
        self.assertEqual(body["success"], True)

    @mock.patch('todo.authenticate.FusionAuthBackend.authenticate')
    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.retrieve_user',
                return_value=mock.Mock(was_successful=lambda: True, status=200,
                                       success_response={"user":{"id":"a718745d-e6bc-45d7-aaec-1ca45d417bb4","twoFactor":{"methods":[{"id": "test"}]}}}))
    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.disable_two_factor',
                return_value=mock.Mock(was_successful=lambda: True, status=200, success_response={}))
    def test_toggle_two_factor_off(self, mock1, mock2, mock3):
        mock3.return_value = self.user
        c = Client()
        logged_in = c.login(username="a718745d-e6bc-45d7-aaec-1ca45d417bb4", password="temporary")
        self.assertEqual(logged_in, True)
        response = c.post(
            '/api/user/toggle-two-factor',
            dumps({"enableTwoFactor": False, "code": "test", "secret": "test"}),
            content_type="application/json"
        )
        body = loads(response.content)
        self.assertLess(response.status_code, 300)
        self.assertEqual(body["success"], True)

    @mock.patch('todo.authenticate.FusionAuthBackend.authenticate')
    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.retrieve_user',
                return_value=mock.Mock(was_successful=lambda: True, status=200,
                                       success_response={"user":{"id":"a718745d-e6bc-45d7-aaec-1ca45d417bb4"}}))
    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.update_user',
                return_value=mock.Mock(was_successful=lambda: True, status=200, success_response={}))
    def test_change_email(self, mock1, mock2, mock3):
        mock3.return_value = self.user
        c = Client()
        logged_in = c.login(username="a718745d-e6bc-45d7-aaec-1ca45d417bb4", password="temporary")
        self.assertEqual(logged_in, True)
        response = c.post(
            '/api/user/change-email',
            dumps({"newEmail": "test"}),
            content_type="application/json"
        )
        body = loads(response.content)
        self.assertLess(response.status_code, 300)
        self.assertEqual(body["success"], True)

    @mock.patch('todo.authenticate.FusionAuthBackend.authenticate')
    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.login',
                return_value=mock.Mock(was_successful=lambda: True, status=200))
    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.retrieve_user',
                return_value=mock.Mock(was_successful=lambda: True, status=200,
                                       success_response={"user":{"id":"a718745d-e6bc-45d7-aaec-1ca45d417bb4","email":"test"}}))
    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.update_user',
                return_value=mock.Mock(was_successful=lambda: True, status=200, success_response={}))
    def test_change_password_success(self, mock1, mock2, mock3, mock4):
        mock4.return_value = self.user
        c = Client()
        logged_in = c.login(username="a718745d-e6bc-45d7-aaec-1ca45d417bb4", password="temporary")
        self.assertEqual(logged_in, True)
        response = c.post(
            '/api/user/change-password',
            dumps({"currentPassword": "test", "newPassword": "test"}),
            content_type="application/json"
        )
        body = loads(response.content)
        self.assertLess(response.status_code, 300)
        self.assertEqual(body["success"], True)

    @mock.patch('todo.authenticate.FusionAuthBackend.authenticate')
    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.login',
                return_value=mock.Mock(was_successful=lambda: True, status=401))
    @mock.patch('fusionauth.fusionauth_client.FusionAuthClient.retrieve_user',
                return_value=mock.Mock(was_successful=lambda: True, status=200,
                                       success_response={"user":{"id":"a718745d-e6bc-45d7-aaec-1ca45d417bb4","email":"test"}}))
    def test_change_password_success(self, mock1, mock2, mock3):
        mock3.return_value = self.user
        c = Client()
        logged_in = c.login(username="a718745d-e6bc-45d7-aaec-1ca45d417bb4", password="temporary")
        self.assertEqual(logged_in, True)
        response = c.post(
            '/api/user/change-password',
            dumps({"currentPassword": "test", "newPassword": "test"}),
            content_type="application/json"
        )
        body = loads(response.content)
        self.assertLess(response.status_code, 300)
        self.assertEqual(body["success"], False)
