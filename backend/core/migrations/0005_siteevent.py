from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("core", "0004_project_portfolio_metadata")]

    operations = [
        migrations.CreateModel(
            name="SiteEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=40)),
                ("location", models.CharField(max_length=40)),
                ("path", models.CharField(max_length=255)),
                ("lang", models.CharField(max_length=2)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={"ordering": ["-created_at"], "verbose_name": "Событие сайта", "verbose_name_plural": "События сайта"},
        ),
    ]
