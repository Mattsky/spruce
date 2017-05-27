import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','first_project.settings')

import django
django.setup()

## Fake population script

import random
from app_two.models import User
from faker import Faker

fakegen = Faker()

def populate(N=5):
	for entry in range(N):

		# create fake data for entry

		fake_first_name = fakegen.first_name()
		fake_last_name = fakegen.last_name()
		fake_email = fakegen.email()

		# create the new user entry

		userinfo = User.objects.get_or_create(first_name=fake_first_name,last_name=fake_last_name,email=fake_email)
		#userinfo.save()

if __name__ == '__main__':
	print("Populating script!")
	populate(20)
	print("Population complete!")
