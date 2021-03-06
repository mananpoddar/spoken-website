# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Third Party Stuff
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MdlEnrol',
            fields=[
                ('id', models.BigIntegerField(serialize=False, primary_key=True)),
                ('enrol', models.CharField(max_length=60)),
                ('status', models.BigIntegerField()),
                ('courseid', models.BigIntegerField()),
                ('sortorder', models.BigIntegerField()),
                ('name', models.CharField(max_length=765, blank=True)),
                ('enrolperiod', models.BigIntegerField(null=True, blank=True)),
                ('enrolstartdate', models.BigIntegerField(null=True, blank=True)),
                ('enrolenddate', models.BigIntegerField(null=True, blank=True)),
                ('expirynotify', models.IntegerField(null=True, blank=True)),
                ('expirythreshold', models.BigIntegerField(null=True, blank=True)),
                ('notifyall', models.IntegerField(null=True, blank=True)),
                ('password', models.CharField(max_length=150, blank=True)),
                ('cost', models.CharField(max_length=60, blank=True)),
                ('currency', models.CharField(max_length=9, blank=True)),
                ('roleid', models.BigIntegerField(null=True, blank=True)),
                ('customint1', models.BigIntegerField(null=True, blank=True)),
                ('customint2', models.BigIntegerField(null=True, blank=True)),
                ('customint3', models.BigIntegerField(null=True, blank=True)),
                ('customint4', models.BigIntegerField(null=True, blank=True)),
                ('customint5', models.BigIntegerField(null=True, blank=True)),
                ('customint6', models.BigIntegerField(null=True, blank=True)),
                ('customint7', models.BigIntegerField(null=True, blank=True)),
                ('customint8', models.BigIntegerField(null=True, blank=True)),
                ('customchar1', models.CharField(max_length=765, blank=True)),
                ('customchar2', models.CharField(max_length=765, blank=True)),
                ('customchar3', models.CharField(max_length=3999, blank=True)),
                ('customdec1', models.DecimalField(null=True, max_digits=14, decimal_places=7, blank=True)),
                ('customdec2', models.DecimalField(null=True, max_digits=14, decimal_places=7, blank=True)),
                ('customtext1', models.TextField(blank=True)),
                ('customtext2', models.TextField(blank=True)),
                ('customtext3', models.TextField(blank=True)),
                ('customtext4', models.TextField(blank=True)),
                ('timecreated', models.BigIntegerField()),
                ('timemodified', models.BigIntegerField()),
            ],
            options={
                'db_table': 'mdl_enrol',
            },
        ),
        migrations.CreateModel(
            name='MdlQuizAttempts',
            fields=[
                ('id', models.BigIntegerField(serialize=False, primary_key=True)),
                ('quiz', models.BigIntegerField()),
                ('userid', models.BigIntegerField()),
                ('attempt', models.IntegerField(unique=True)),
                ('uniqueid', models.BigIntegerField(unique=True)),
                ('layout', models.TextField()),
                ('currentpage', models.BigIntegerField()),
                ('preview', models.IntegerField()),
                ('state', models.CharField(max_length=48)),
                ('timestart', models.BigIntegerField()),
                ('timefinish', models.BigIntegerField()),
                ('timemodified', models.BigIntegerField()),
                ('timecheckstate', models.BigIntegerField(null=True, blank=True)),
                ('sumgrades', models.DecimalField(null=True, max_digits=12, decimal_places=5, blank=True)),
                ('needsupgradetonewqe', models.IntegerField()),
            ],
            options={
                'db_table': 'mdl_quiz_attempts',
            },
        ),
        migrations.CreateModel(
            name='MdlQuizGrades',
            fields=[
                ('id', models.BigIntegerField(serialize=False, primary_key=True)),
                ('quiz', models.BigIntegerField()),
                ('userid', models.BigIntegerField()),
                ('grade', models.DecimalField(max_digits=12, decimal_places=5)),
                ('timemodified', models.BigIntegerField()),
            ],
            options={
                'db_table': 'mdl_quiz_grades',
            },
        ),
        migrations.CreateModel(
            name='MdlRoleAssignments',
            fields=[
                ('id', models.BigIntegerField(serialize=False, primary_key=True)),
                ('roleid', models.BigIntegerField()),
                ('contextid', models.BigIntegerField()),
                ('userid', models.BigIntegerField()),
                ('timemodified', models.BigIntegerField()),
                ('modifierid', models.BigIntegerField()),
                ('component', models.CharField(max_length=300)),
                ('itemid', models.BigIntegerField()),
                ('sortorder', models.BigIntegerField()),
            ],
            options={
                'db_table': 'mdl_role_assignments',
            },
        ),
        migrations.CreateModel(
            name='MdlUser',
            fields=[
                ('id', models.BigIntegerField(serialize=False, primary_key=True)),
                ('auth', models.CharField(max_length=60)),
                ('confirmed', models.IntegerField()),
                ('gender', models.CharField(default=b'0', max_length=100, null=True, blank=True)),
                ('age_range', models.CharField(default=b'0', max_length=100, null=True, blank=True)),
                ('academic_code', models.CharField(default=b'0', max_length=100, null=True, blank=True)),
                ('organizer', models.CharField(default=b'0', max_length=100, null=True, blank=True)),
                ('invigilator', models.CharField(default=b'0', max_length=100, null=True, blank=True)),
                ('flag', models.CharField(default=b'0', max_length=100, null=True, blank=True)),
                ('mnethostid', models.BigIntegerField(unique=True)),
                ('username', models.CharField(unique=True, max_length=255)),
                ('password', models.CharField(max_length=96)),
                ('idnumber', models.CharField(max_length=765)),
                ('firstname', models.CharField(max_length=300)),
                ('lastname', models.CharField(max_length=300)),
                ('email', models.CharField(max_length=300)),
                ('icq', models.CharField(max_length=45)),
                ('skype', models.CharField(max_length=150)),
                ('yahoo', models.CharField(max_length=150)),
                ('aim', models.CharField(max_length=150)),
                ('msn', models.CharField(max_length=150)),
                ('phone1', models.CharField(max_length=60)),
                ('phone2', models.CharField(max_length=60)),
                ('institution', models.CharField(max_length=120)),
                ('department', models.CharField(max_length=90)),
                ('address', models.CharField(max_length=210)),
                ('city', models.CharField(max_length=360)),
                ('country', models.CharField(max_length=6)),
                ('theme', models.CharField(max_length=150)),
                ('timezone', models.CharField(max_length=300)),
                ('lastip', models.CharField(max_length=135)),
                ('secret', models.CharField(max_length=45)),
                ('url', models.CharField(max_length=765)),
                ('description', models.TextField(blank=True)),
                ('imagealt', models.CharField(max_length=765, blank=True)),
            ],
            options={
                'db_table': 'mdl_user',
            },
        ),
        migrations.CreateModel(
            name='MdlUserEnrolments',
            fields=[
                ('id', models.BigIntegerField(serialize=False, primary_key=True)),
                ('status', models.BigIntegerField()),
                ('enrolid', models.BigIntegerField()),
                ('userid', models.BigIntegerField()),
                ('timestart', models.BigIntegerField()),
                ('timeend', models.BigIntegerField()),
                ('modifierid', models.BigIntegerField()),
                ('timecreated', models.BigIntegerField()),
                ('timemodified', models.BigIntegerField()),
            ],
            options={
                'db_table': 'mdl_user_enrolments',
            },
        ),
    ]
