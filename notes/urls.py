from django.urls import path

from . import views

urlpatterns = [
    path('notes', views.NotesListView.as_view(), name='notes.list'),
    path('tags/create', views.create_tag, name='tags.create'),
    path('community', views.CommunityView.as_view(), name='community'),
    path('inbox', views.InboxView.as_view(), name='inbox'),
    path('messages/send', views.send_message, name='messages.send'),
    path('profile', views.ProfileUpdateView.as_view(), name='profile'),
    path('people/<str:username>', views.ProfileDetailView.as_view(), name='profile.detail'),
    path('notes/online', views.online_users, name='notes.online'),
    path('notes/<int:note_id>/share-links', views.share_links, name='notes.share_links'),
    path('notes/<int:note_id>/share-links/<int:link_id>/revoke', views.revoke_share_link, name='notes.share_links.revoke'),
    path('notes/<int:note_id>/share-users', views.share_user, name='notes.share_users'),
    path('notes/<int:note_id>/collaborators', views.share_collaborator, name='notes.collaborators'),
    path('notes/<int:note_id>/share-groups', views.share_group, name='notes.share_groups.share'),
    path('notes/groups', views.share_groups, name='notes.share_groups'),
    path('notes/groups/<int:group_id>/members', views.share_group_members, name='notes.share_groups.members'),
    path('notes/<int:pk>', views.NotesDetailView.as_view(), name='notes.detail'),
    path('notes/new', views.NotesCreateView.as_view(), name='notes.new'),
    path('notes/<int:pk>/edit', views.NotesUpdateView.as_view(), name='notes.update'),
    path('notes/<int:pk>/delete', views.NotesDeleteView.as_view(), name='notes.delete')
]