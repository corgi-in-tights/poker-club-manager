from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from poker_club_manager.users.models import User

from .serializers import UserSerializer


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "username"

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False)
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(detail=False, url_path="fetch-matching-names")
    def fetch_matching_names(self, request):
        requested_query = request.query_params.get("query", "").strip()
        if not requested_query:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"detail": "Query parameter 'query' is required."},
            )

        users = (
            User.objects
            .only("id", "username", "name")
            .filter_by_name(requested_query)[:3]
        )
        serializer = UserSerializer(users, many=True, context={"request": request})

        return Response(
            status=status.HTTP_200_OK,
            data={"results": serializer.data},
        )
