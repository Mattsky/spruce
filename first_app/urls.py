from django.conf.urls import url
from first_app import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^held/$', views.held, name='held'),
    url(r'^updates/$', views.updates, name='updates'),
    url(r'^installed/$', views.installed, name='installed'),
    url(r'^scan/$', views.scan, name='scan'),
    url(r'^sshtest/$', views.sshtest, name='sshtest'),
]
