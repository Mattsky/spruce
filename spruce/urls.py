# Spruce - a tool to help manage system software states.
# Copyright (C) 2017 Matt North

# This file is part of Spruce.

# Spruce is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Spruce is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Spruce.  If not, see <http://www.gnu.org/licenses/>.

from django.conf.urls import url
from spruce import views
from django.contrib import admin
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', auth_views.login, {'template_name': 'spruce/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'spruce/login.html'}, name='logout'),
    url(r'^held/$', views.held, name='held'),
    url(r'^updates/$', views.updates, name='updates'),
    url(r'^installed/$', views.installed, name='installed'),
    url(r'^scan/$', views.scan, name='scan'),
    url(r'^upload_file/$', views.upload_file, name='upload_file'),
    url(r'^update_history/$', views.update_history, name='update_history'),
]
