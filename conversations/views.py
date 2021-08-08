from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http.response import Http404
from django.shortcuts import redirect, reverse
from django.views.generic import DetailView
from users import models as user_models
from users import mixins as user_mixins
from . import models


@login_required
def go_conversation(request, host_pk, guest_pk):
    host = user_models.User.objects.get_or_none(pk=host_pk)
    guest = user_models.User.objects.get_or_none(pk=guest_pk)
    if host is not None and guest is not None:
        try:
            conversation = models.Conversation.objects.get(
                Q(participants=host) & Q(participants=guest)
            )
        except models.Conversation.DoesNotExist:
            conversation = models.Conversation.objects.create()
            conversation.participants.add(host, guest)
        return redirect(reverse("conversations:detail", kwargs={"pk": conversation.pk}))
    else:
        raise Http404()


class ConversationDetailView(user_mixins.LoggedInOnlyView, DetailView):
    model = models.Conversation

    def get_object(self, *args, **kwargs):
        obj = super().get_object(*args, **kwargs)
        if self.request.user not in obj.participants.all():
            raise Http404()
        return obj

    def post(self, *args, **kwargs):
        message = self.request.POST.get("message", None)
        pk = kwargs.get("pk")
        conversation = models.Conversation.objects.get_or_none(pk=pk)
        if not conversation:
            raise Http404()
        if message is not None:
            models.Message.objects.create(
                message=message, user=self.request.user, conversation=conversation
            )
        return redirect(reverse("conversations:detail", kwargs={"pk": pk}))
