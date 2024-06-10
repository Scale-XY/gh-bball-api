from random import choice

from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import update_session_auth_hash
from django.conf import settings
from django.contrib.auth.models import Group

from rest_framework import generics
from rest_framework.response import Response

from .serializers import (
    RegisterSerializer,
    UserSerializer,
    UserSerializerWithToken,
    SetUserSerializer,
    GroupSerializer,
)
from .serializers import (
    ChangePasswordSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    CreateUserSerializer,
)

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from rest_framework.test import APIRequestFactory
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework import viewsets

from .models import User, PasswordResetToken, UserInvitation
from .permissions import IsSuperUser, IsOwner


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Convert user groups to a list of group names
        groups = [group.name for group in user.groups.all()]

        token["username"] = user.username
        token["full_name"] = user.name
        token["groups"] = groups
        token["id"] = user.id

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        serializer = UserSerializerWithToken(self.user).data
        for k, v in serializer.items():
            data[k] = v

        return data


class MyTokenObtainPairView(TokenObtainPairView):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = MyTokenObtainPairSerializer


# Register API
class RegisterApi(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = ()
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        # add a tenant context
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "user": UserSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "message": "User Created Successfully.  Now perform Login to get your token",
            }
        )


class SetAccountView(generics.GenericAPIView):
    permission_classes = ()
    authentication_classes = ()

    serializer_class = SetUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            queryset = UserInvitation.objects.filter(key=request.GET.get("token"))

            if queryset.exists():
                user_invitation = queryset.first()

                # if user_invitation.timestamp < timezone.now() - timezone.timedelta(minutes=30):
                #     # expired
                #     user_invitation.delete()
                #     return Response({"error": "Password reset key is expired! Reset your email again."}, status= status.HTTP_404_NOT_FOUND)

                # else:

                # seting up the password
                password = serializer.data["password"]

                user = user_invitation.user
                user.set_password(password)
                user.save()

                # delete the data in our database
                user_invitation.delete()

                return Response(
                    {"success": "Password updated successfully."},
                    status=status.HTTP_200_OK,
                )

            else:
                # invalid key
                return Response(
                    {"error": "Invalid key"}, status=status.HTTP_404_NOT_FOUND
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# change password
class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            update_session_auth_hash(request, user)

            # uses APIRequestFactory to "test" the token obtain view and get the new token for our users' when password changed
            get_token_params = {
                "email": request.user.email,
                "password": serializer.data["new_password1"],
            }
            factory = APIRequestFactory()
            token_request = factory.post(
                "/users/token/", get_token_params
            )  # converts our dict param to httprequest object
            response = MyTokenObtainPairView.as_view()(
                request=token_request
            )  # calls our own token obtain pair view

            # returns the token and other details to client to use it in authentication
            return Response(response.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Reset password
class PasswordResetRequestView(generics.GenericAPIView):
    permission_classes = ()
    authentication_classes = ()

    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check if email address already requested a password reset
            if not User.objects.filter(
                email__iexact=serializer.data["email"].lower()
            ).exists():
                payload = {
                    "message": "Email does not exists."  #'The e-mail address ('+ serializer.data['email'] +') has already set up an account.'
                }

                return Response(payload, status=status.HTTP_406_NOT_ACCEPTABLE)

            user = User.objects.filter(email__iexact=serializer.data["email"]).first()

            if PasswordResetToken.objects.filter(user=user).exists():
                payload = {
                    "message": "The e-mail address ("
                    + serializer.data["email"]
                    + ") has already been sent a password reset link."
                }
                return Response(payload, status=status.HTTP_406_NOT_ACCEPTABLE)

            password_reset = PasswordResetToken.objects.filter(user=user).first()

            # checking for last password reset
            # if password_reset.timestamp < timezone.now() - timezone.timedelta(days=1):
            # password is not recently updated
            # password_reset.delete()
            key = "".join(
                [
                    choice(
                        "!@$_-qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"
                    )
                    for i in range(99)
                ]
            )

            password_reset = PasswordResetToken(
                user=user,
                key=key,
                url="{}?token={}".format(
                    f"{settings.FRONTEND_HOST_URL}/reset-password", key
                ),
            )
            password_reset.save()

            payload = {
                "message": "Password reset link sent to {}.".format(
                    serializer.data["email"]
                )
            }

            return Response(payload, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)


class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = ()
    authentication_classes = ()

    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            queryset = PasswordResetToken.objects.filter(key=request.GET.get("token"))

            if queryset.exists():
                password_reset = queryset.first()

                if password_reset.timestamp < timezone.now() - timezone.timedelta(
                    minutes=30
                ):
                    # expired
                    password_reset.delete()
                    return Response(
                        {
                            "error": "Password reset key is expired! Reset your email again."
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )

                else:
                    # seting up the password
                    password = serializer.data["new_password1"]

                    user = password_reset.user
                    user.set_password(password)
                    user.save()

                    # delete the data in our database
                    password_reset.delete()
                    return Response(
                        {"success": "Password updated successfully."},
                        status=status.HTTP_200_OK,
                    )

            else:
                # invalid key
                return Response(
                    {"error": "Invalid key"}, status=status.HTTP_404_NOT_FOUND
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupViewSet(viewsets.ModelViewSet):
    pagination_class = None
    serializer_class = GroupSerializer

    def get_queryset(self):
        # Get the user's requested selling platform from the request data
        user = self.request.user
        if user.is_superuser:
            # If the user is staff, return all UserMission objects
            return Group.objects.all()
        else:
            # Only return the groups of the user
            return user.groups.all()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer
    http_method_names = ["get", "head", "options", "trace", "put", "patch", "post"]

    def list(self, request, *args, **kwargs):
        # You can perform custom logic here

        user = self.request.user
        if user.is_superuser:
            queryset = User.objects.all().order_by("id")
        elif user.is_staff:
            queryset = User.objects.filter(groups__in=user.groups.all()).order_by("id")
        else:
            return Response(
                {"user": ["Only administrator can access this"]},
                status=status.HTTP_403_FORBIDDEN,
            )

        serialized_data = UserSerializer(queryset, many=True)
        return Response(serialized_data.data)

    @action(detail=False, methods=["GET"])
    def all_emails(self, request):
        # Get the currently authenticated user's data
        emails = User.objects.values_list("email", flat=True)
        # Return the list of emails
        return Response({"emails": emails})

    @action(detail=False, methods=["GET"])
    def me(self, request):
        # Get the currently authenticated user's data
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=["POST"], serializer_class=CreateUserSerializer)
    def create_user(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Save the user without committing to the database

            temp_password = User.objects.make_random_pass()

            # Access validated data from the serializer
            user_data = serializer.validated_data
            user = User(
                name=user_data.get("name", ""),
                email=user_data["email"],
                is_staff=user_data.get("is_staff", False),
            )

            # Set the password for the user
            user.set_password(temp_password)

            # Save the user to the database
            user.save()

            # Set the groups for the user using the set() method
            groups = user_data.get("groups", [])
            user.groups.set(groups)

            if UserInvitation.objects.filter(user=user).exists():
                payload = {
                    "message": "The e-mail address ("
                    + serializer.data["email"]
                    + ") has already been sent a password reset link."
                }
                return Response(payload, status=status.HTTP_406_NOT_ACCEPTABLE)

            key = "".join(
                [
                    choice(
                        "!@$_-qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"
                    )
                    for i in range(99)
                ]
            )

            user_invitation = UserInvitation(
                user=user,
                key=key,
                invited_by=request.user,
                url="{}?token={}".format(
                    f"{settings.FRONTEND_HOST_URL}/set-account", key
                ),
            )
            user_invitation.save()

            payload = {
                "message": "Password reset link sent to {}.".format(
                    serializer.data["email"]
                ),
                "temporary_password": "The temporary password for the account is {}".format(
                    temp_password
                ),
            }

            return Response(payload, status=status.HTTP_201_CREATED)
        else:
            # Return a response with serializer errors if the input data is invalid
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # only authenticated users can view their own user record
    # superusers can view all user records
    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action == "retrieve":
            # only owner or superuser can retrieve a user
            permission_classes += [IsSuperUser | IsOwner]
        return [permission() for permission in permission_classes]
