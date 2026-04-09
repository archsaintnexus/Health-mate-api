from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_companyuser_state_and_update_emergencycontact_fields"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="companyuser",
                name="phone_number",
        ),
    ]
