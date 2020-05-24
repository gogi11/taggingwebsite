from django.conf.urls import url
from django.contrib.auth import views
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from frontend.views import signup

urlpatterns = [
    url('home', TemplateView.as_view(template_name="home_template.html"), name="home"),
    url(r'^login/$', views.LoginView.as_view(template_name='login_template.html'), name='login'),
    url(r'^register/$', signup, name='register'),
    url(r'^logout/$', views.LogoutView.as_view(next_page=reverse_lazy("home")), name='logout'),
]
