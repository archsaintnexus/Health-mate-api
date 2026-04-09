from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_medicalinformation_emergencycontact"),
    ]

    operations = [
        migrations.AddField(
            model_name="companyuser",
            name="state",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.RenameField(
            model_name="emergencycontact",
            old_name="name",
            new_name="next_of_kin_name",
        ),
        migrations.RenameField(
            model_name="emergencycontact",
            old_name="phone_number",
            new_name="next_of_kin_phone",
        ),
        migrations.AlterField(
            model_name="emergencycontact",
            name="next_of_kin_name",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="emergencycontact",
            name="relationship",
            field=models.CharField(max_length=100),
        ),
        migrations.RemoveField(
            model_name="emergencycontact",
            name="number_of_next_of_kin",
        ),
    ]
