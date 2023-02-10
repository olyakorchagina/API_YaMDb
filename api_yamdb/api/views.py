from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title, User

from api_yamdb.settings import EMAIL_ADMIN

from .filters import TitleFilter
from .mixins import CreateListDestroyViewSet
from .permissions import (IsAdminOrReadOnly, IsAdminOrStaff,
                          IsAuthorOrAdminOrModerator)
from .serializers import (AuthSignUpSerializer, AuthTokenSerializer,
                          CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleReadSerializer, TitleWriteSerializer,
                          UserSerializer)


class TitleViewSet(ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('name').all()
    permission_classes = (IsAdminOrReadOnly,)
    filterset_class = TitleFilter
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH',):
            return TitleWriteSerializer
        return TitleReadSerializer


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrAdminOrModerator,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrAdminOrModerator,)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrStaff,)
    search_fields = ('=username',)
    lookup_field = 'username'

    @action(
        detail=False,
        methods=['GET', 'PATCH'],
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def signup(request):
    username = request.data.get('username')

    if not User.objects.filter(username=username).exists():
        serializer = AuthSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        send_confirmation_code(username)
        return Response(serializer.data, status=status.HTTP_200_OK)

    user = get_object_or_404(User, username=username)
    serializer = AuthSignUpSerializer(
        user, data=request.data, partial=True
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    send_confirmation_code(username)
    return Response(serializer.data, status=status.HTTP_200_OK)


def send_confirmation_code(username):
    user = get_object_or_404(User, username=username)
    confirmation_code = default_token_generator.make_token(user)
    user.confirmation_code = confirmation_code
    send_mail(
        'Код регистрации',
        f'Код для получения токена {user.confirmation_code}',
        EMAIL_ADMIN,
        [user.email],
        fail_silently=False,
    )
    user.save()


@api_view(['POST'])
@permission_classes((AllowAny,))
def get_token(request):
    serializer = AuthTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    confirmation_code = serializer.validated_data['confirmation_code']
    user = get_object_or_404(User, username=username)
    if user.confirmation_code == confirmation_code:
        refresh = RefreshToken.for_user(user)
        token_data = {'token': str(refresh.access_token)}
        return Response(token_data, status=status.HTTP_200_OK)
    return Response(
        'Неверный код подтверждения', status=status.HTTP_400_BAD_REQUEST
    )
