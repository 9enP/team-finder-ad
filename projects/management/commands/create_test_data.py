from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from projects.models import Project

User = get_user_model()


def get_or_create_user(email, password, name, surname, **extra_fields):
    """
    Idempotent user creation: User requires avatar from create_user,
    so we use lookup + create_user instead of ORM get_or_create on User.
    """
    normalized = User.objects.normalize_email(email)
    existing = User.objects.filter(email=normalized).first()
    if existing:
        return existing, False
    user = User.objects.create_user(
        email=normalized,
        name=name,
        surname=surname,
        password=password,
        **extra_fields,
    )
    return user, True


def get_or_create_project(owner, name, description, status):
    project, created = Project.objects.get_or_create(
        owner=owner,
        name=name,
        defaults={
            "description": description,
            "status": status,
            "github_url": "",
        },
    )
    return project, created


class Command(BaseCommand):
    help = "Создаёт тестовых пользователей, проекты, участников и избранное (идемпотентно)."

    def handle(self, *args, **options):
        projects_created = 0

        admin_email = User.objects.normalize_email("admin@admin.com")
        if not User.objects.filter(email=admin_email).exists():
            User.objects.create_superuser(
                email=admin_email,
                name="Admin",
                surname="Admin",
                password="admin",
            )
            self.stdout.write("Создан суперпользователь admin@admin.com")
        else:
            self.stdout.write("Суперпользователь admin@admin.com уже существует")

        maria, _ = get_or_create_user(
            "maria@example.com",
            "password123",
            "Мария",
            "Петрова",
            about="Fullstack разработчик",
            phone="+79991234567",
        )
        alex, _ = get_or_create_user(
            "alex@example.com",
            "password123",
            "Алексей",
            "Иванов",
            about="Backend разработчик на Python",
            phone="+79997654321",
        )
        kate, _ = get_or_create_user(
            "kate@example.com",
            "password123",
            "Екатерина",
            "Смирнова",
            about="UI/UX дизайнер",
            phone="+79995551234",
        )

        p_maria_1, c = get_or_create_project(
            maria,
            "Платформа для фриланса",
            "Маркетплейс для поиска фриланс-заказов",
            "open",
        )
        projects_created += int(c)

        p_maria_2, c = get_or_create_project(
            maria,
            "Трекер привычек",
            "Приложение для отслеживания полезных привычек",
            "closed",
        )
        projects_created += int(c)

        p_alex_1, c = get_or_create_project(
            alex,
            "Open Source CMS",
            "Система управления контентом на Django",
            "open",
        )
        projects_created += int(c)

        p_alex_2, c = get_or_create_project(
            alex,
            "API для погоды",
            "Сервис агрегации погодных данных",
            "open",
        )
        projects_created += int(c)

        p_kate_1, c = get_or_create_project(
            kate,
            "Портфолио конструктор",
            "Конструктор портфолио для дизайнеров",
            "open",
        )
        projects_created += int(c)

        p_kate_2, c = get_or_create_project(
            kate,
            "Дизайн-система",
            "Библиотека компонентов в Figma и React",
            "open",
        )
        projects_created += int(c)

        p_maria_1.participants.add(maria, alex, kate)
        p_maria_2.participants.add(maria)
        p_alex_1.participants.add(alex, maria, kate)
        p_alex_2.participants.add(alex)
        p_kate_1.participants.add(kate, alex)
        p_kate_2.participants.add(kate)

        maria.favorites.add(p_alex_1, p_kate_1)
        alex.favorites.add(p_maria_1)
        kate.favorites.add(p_alex_2)

        self.stdout.write(self.style.SUCCESS("✓ Тестовые данные успешно созданы"))
        self.stdout.write(
            "  Пользователи: admin@admin.com/admin, maria@example.com/password123, "
            "alex@example.com/password123, kate@example.com/password123"
        )
        self.stdout.write(f"  Проектов создано: {projects_created}")
