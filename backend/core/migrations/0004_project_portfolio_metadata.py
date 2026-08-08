from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("core", "0003_aiproviderconfig_project_ai_notes_and_more")]

    operations = [
        migrations.AddField(
            model_name="project",
            name="client",
            field=models.CharField(blank=True, max_length=160),
        ),
        migrations.AddField(
            model_name="project",
            name="highlights",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="project",
            name="project_state",
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name="project",
            name="source_group",
            field=models.CharField(blank=True, max_length=80),
        ),
    ]
