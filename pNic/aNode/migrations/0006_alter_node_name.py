# Generated by Django 4.1.6 on 2023-03-06 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("aNode", "0005_edge_payload_node_payload"),
    ]

    operations = [
        migrations.AlterField(
            model_name="node",
            name="name",
            field=models.CharField(max_length=128),
        ),
    ]
