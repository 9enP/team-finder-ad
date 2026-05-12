import uuid

from django.contrib.auth import get_user
from django.test import Client, TestCase

from projects.models import Project
from users.models import User


def _unique_email(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}@test.com"


class ProjectListViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email=_unique_email("owner"),
            name="Owner",
            surname="User",
            password="pass12345",
            phone="+79991110001",
        )

    def test_project_list_returns_200(self):
        Project.objects.create(
            owner=self.owner,
            name="Visible Project",
            description="",
            status="open",
        )
        response = Client().get("/projects/list/")
        self.assertEqual(response.status_code, 200)

    def test_project_list_pagination_15_projects_12_per_page(self):
        for i in range(15):
            Project.objects.create(
                owner=self.owner,
                name=f"Bulk Project {i}",
                description="",
                status="open",
            )
        c = Client()
        page1 = c.get("/projects/list/")
        self.assertEqual(page1.status_code, 200)
        self.assertEqual(len(page1.context["projects"]), 12)

        page2 = c.get("/projects/list/?page=2")
        self.assertEqual(page2.status_code, 200)
        self.assertEqual(len(page2.context["projects"]), 3)


class ProjectDetailViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email=_unique_email("pdetail"),
            name="O",
            surname="W",
            password="pass12345",
            phone="+79991110002",
        )
        self.project = Project.objects.create(
            owner=self.owner,
            name="Detail Me",
            description="desc",
            status="open",
        )

    def test_project_detail_returns_200(self):
        response = Client().get(f"/projects/{self.project.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["project"].pk, self.project.pk)


class UserDetailViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=_unique_email("udetail"),
            name="U",
            surname="D",
            password="pass12345",
            phone="+79991110003",
        )

    def test_user_detail_returns_200(self):
        response = Client().get(f"/users/{self.user.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["user"].pk, self.user.pk)


class RegisterViewTests(TestCase):
    def test_register_auto_login_and_redirect(self):
        email = _unique_email("reg")
        c = Client()
        response = c.post(
            "/users/register/",
            {
                "name": "Reg",
                "surname": "User",
                "email": email,
                "password": "password123",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(get_user(c).is_authenticated)
        self.assertTrue(
            any("/projects/list/" in str(url) for url, _ in response.redirect_chain)
        )


class LoginLogoutViewTests(TestCase):
    def setUp(self):
        self.email = _unique_email("login")
        self.password = "secretpass99"
        User.objects.create_user(
            email=self.email,
            name="L",
            surname="I",
            password=self.password,
            phone="+79991110004",
        )

    def test_login_and_logout(self):
        c = Client()
        c.post(
            "/users/login/",
            {"email": self.email, "password": self.password},
            follow=True,
        )
        self.assertTrue(get_user(c).is_authenticated)

        c.get("/users/logout/")
        self.assertFalse(get_user(c).is_authenticated)

    def test_login_invalid_credentials(self):
        c = Client()
        response = c.post(
            "/users/login/",
            {"email": self.email, "password": "wrong-password"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Неверный имейл или пароль")
        self.assertFalse(get_user(c).is_authenticated)
