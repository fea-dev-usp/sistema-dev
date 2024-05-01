from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("calendar", views.calendar, name="calendar"),
    path("profile", views.profile, name="profile"),
    path("search", views.search, name="search"),
    path("display/<str:type_info>/<int:id>", views.display, name="display"),
    path("bio", views.bio, name="bio"),
    path("create-view/<str:intention>", views.create_view, name="create_view"),
    path("create/<str:intention>", views.create, name="create"),
    path("meeting", views.meeting, name="meeting"),
    path("meeting/<int:reuniao_id>/<str:type_info>", views.meeting_duration, name="meeting_duration"),
    path("ranking", views.ranking, name="ranking"),
]