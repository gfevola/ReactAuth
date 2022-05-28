# Generated by Django 4.0 on 2022-03-05 22:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0004_alter_employee_state_deptid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='empdates',
            name='Status',
            field=models.CharField(choices=[('hire', 'HIRE'), ('term', 'TERMINATION'), ('entry', 'Entry'), ('transfer', 'TRANSFER'), ('promo', 'PROMOTION')], default='entry', max_length=50),
        ),
        migrations.AlterField(
            model_name='employee_state',
            name='Status',
            field=models.CharField(choices=[('hire', 'HIRE'), ('term', 'TERMINATION'), ('entry', 'Entry'), ('transfer', 'TRANSFER'), ('promo', 'PROMOTION')], default='entry', max_length=50),
        ),
    ]