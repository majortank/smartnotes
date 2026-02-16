from django.urls import path

from . import views

urlpatterns = [
    path('notes', views.NotesListView.as_view(), name='notes.list'),
    path('notes/online', views.online_users, name='notes.online'),
    path('notes/<int:note_id>/share-links', views.share_links, name='notes.share_links'),
    path('notes/<int:note_id>/share-links/<int:link_id>/revoke', views.revoke_share_link, name='notes.share_links.revoke'),
    path('notes/groups', views.share_groups, name='notes.share_groups'),
    path('notes/groups/<int:group_id>/members', views.share_group_members, name='notes.share_groups.members'),
    path('notes/<int:pk>', views.NotesDetailView.as_view(), name='notes.detail'),
    path('notes/new', views.NotesCreateView.as_view(), name='notes.new'),
    path('notes/<int:pk>/edit', views.NotesUpdateView.as_view(), name='notes.update'),
    path('notes/<int:pk>/delete', views.NotesDeleteView.as_view(), name='notes.delete')
]