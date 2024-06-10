from django.core import exceptions
from django.utils.translation import gettext_lazy as _

from rest_framework import  serializers
from rest_framework.permissions import IsAuthenticated

from .models import User, PasswordResetToken
from rest_framework_simplejwt.tokens import RefreshToken

import django.contrib.auth.password_validation as validators
from django.contrib.auth.models import Group

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')


# Register serializer
class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id','email','password')#,'first_name','last_name')
        extra_kwargs = {
            'password':{'write_only': True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['email'],password = validated_data['password'],)
                                        #first_name=validated_data['first_name'],last_name=validated_data['last_name'])
        return user

# User serializer
class UserSerializer(serializers.ModelSerializer):

    groups = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = ('id','email','name','is_superuser','is_staff','date_joined','last_login','groups', 'position')

    def get_groups(self, obj):
        groups = Group.objects.filter(user=obj)
        group_names = [group.name for group in groups]
        return group_names
    
class UserSerializerWithToken(serializers.ModelSerializer):

    access = serializers.SerializerMethodField(read_only=True)
    refresh = serializers.SerializerMethodField(read_only=True)
    groups = serializers.SerializerMethodField(read_only=True)

    class Meta:
        
        model = User
        fields = fields = ('id','email','name','date_joined','access','refresh','last_login','groups', 'is_superuser', 'is_staff') 

    def get_access(self, obj):
        token = RefreshToken.for_user(obj)

        token['username'] = obj.email
        token['full_name'] = obj.name
        token['id'] = obj.id
        return str(token.access_token)
    
    def get_refresh(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token)
    
    def get_groups(self, obj):
        groups = Group.objects.filter(user=obj)
        group_names = [group.name for group in groups]
        return group_names

class SetUserSerializer(serializers.ModelSerializer):
    model = User

    """
    Serializer for setting up an account endpoint.
    """

    password = serializers.CharField(
        min_length=8,
        required=True,
        style={'input_type': 'password'}
        )

    confirm_password = serializers.CharField(
        min_length=8,
        required=True,
        style={'input_type': 'password'}
        )

    class Meta:
        model = User
        fields = ('password', 'confirm_password')

    def validate(self, data):

        # get the password from the data
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        #validates if both password matches
        if password != confirm_password:
            raise serializers.ValidationError("The two password fields didn't match.")
        else:
            errors = dict() 
            try:
                # validate the password and catch the exception
                validators.validate_password(password=password)

            # the exception raised here is different than serializers.ValidationError
            except exceptions.ValidationError as e:
                errors['password'] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)

        return super(SetUserSerializer, self).validate(data)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(min_length=8, write_only=True, required=True, style={'input_type': 'password'})
    new_password1 = serializers.CharField(min_length=8, required=True, style={'input_type': 'password'}) #make this to readable so we can use this in our api view
    new_password2 = serializers.CharField(min_length=8, write_only=True, required=True, style={'input_type': 'password'})

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                _('Your old password was entered incorrectly. Please enter it again.')
            )
        return value

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError({'new_password2': _("The two password fields didn't match.")})
        
        if data['old_password'] == data['new_password1'] and data['old_password'] == data['new_password2']:
            raise serializers.ValidationError(
                _('Your new password cannot be the same as your last old password.')
            )

        validators.validate_password(data['new_password1'], self.context['request'].user)
        return data

    def save(self, **kwargs):
        password = self.validated_data['new_password1']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user

class PasswordResetSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('email',)

class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(min_length=8, required=True, style={'input_type': 'password'}) #make this to readable so we can use this in our api view
    new_password2 = serializers.CharField(min_length=8, write_only=True, required=True, style={'input_type': 'password'})

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError({'new_password2': _("The two password fields didn't match.")})
        else:
            errors = dict() 
            try:
                # validate the password and catch the exception
                validators.validate_password(password=data['new_password1'])

            # the exception raised here is different than serializers.ValidationError
            except exceptions.ValidationError as e:
                errors['password'] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)

        return super(PasswordResetConfirmSerializer, self).validate(data)
    
    

class CreateUserSerializer(serializers.ModelSerializer):
    model = User
    
    class Meta:
        model = User
        fields = ('name', 'email', 'groups', 'is_staff')
        extra_kwargs = {
                        'name': {'required': True},
                        'groups': {'required': True},
                        'is_staff': {'required': True},
                        }
