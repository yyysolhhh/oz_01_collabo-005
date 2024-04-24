from typing import Any, Optional, TypeVar

from django.db.models import Model, QuerySet
from django.shortcuts import render
from django.utils import timezone
from rest_framework import permissions, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.serializers import BaseSerializer

from app.board.models import Post, Schedule
from app.board.permissions import IsWriterOrReadOnly
from app.board.serializers import PostSerializer, ScheduleSerializer
from app.club.models import Club


class PostViewSet(viewsets.ModelViewSet[Post]):
    # queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsWriterOrReadOnly]

    def get_queryset(self) -> Post:
        # club_id: Optional[int] = self.kwargs.get("club_id")
        club_id = self.kwargs.get("club_id")
        if club_id is None:
            raise NotFound(detail="club not found")
        return Post.objects.filter(club_id=club_id).order_by("-created_at")

    # def get_object(self):
    #     club_id = self.kwargs.get("club_id")
    #     try:
    #         club = Club.objects.get(id=club_id)
    #         print("cl", club)
    #         return club
    #     except Club.DoesNotExist:
    #         raise NotFound("Club not found")

    def perform_create(self, serializer: BaseSerializer[Post]) -> None:
        club_id = self.kwargs.get("club_id")
        serializer.save(club_id=club_id, writer=self.request.user)


class ScheduleViewSet(viewsets.ModelViewSet[Schedule]):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsWriterOrReadOnly]

    def get_queryset(self) -> Schedule:
        club_id = self.kwargs.get("club_id")
        if club_id is None:
            raise NotFound(detail="club not found")
        current_datetime = timezone.now()
        return Schedule.objects.filter(club_id=club_id, event_time__gte=current_datetime).order_by("event_time")

    def perform_create(self, serializer: BaseSerializer[Schedule]) -> None:
        club_id = self.kwargs.get("club_id")
        serializer.save(club_id=club_id, writer=self.request.user)
