from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, EmailVerificationCode

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email','phone_number','first_name','last_name']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    password2 = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ['id','username','email','phone_number','first_name','last_name','password','password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password':"passwords dont match"})
        return attrs
        
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        user.is_active = False
        user.save()
        return user
    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'first_name', 'last_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except:
            raise serializers.ValidationError("მომხმარებელი მსგავსი email-ით ვერ მოიძებნა")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only = True, required = True, validators = [validate_password])
    password2 = serializers.CharField(write_only = True, required = True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "პაროლები არ ემთხვევა"})
        
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uidb64']))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, KeyError):
            raise serializers.ValidationError({"message": "რაღაცა არასწორია"})
        
        token = attrs['token']
        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError({'message': 'არასწორია ან ვადაგასული ტოკეინია'})
        
        attrs['user'] = user
        return attrs
    
    def save(self):
        user = self.validated_data['user']
        user.set_password(self.validated_data['password'])
        user.save()


class EmailCodeResendserializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'message': 'მომხმარებელი მსგავსი email ით ვერ მოიძებნა'})
        
        if user.is_active:
            raise serializers.ValidationError({"message": "მომხმარებელი უკვე აქტიურია"})
        
        attrs['user'] = user
        return attrs
    

class EmailcoedConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()

    def validate(self, attrs):
        email = attrs['email']
        code = attrs['code']

        try:
            user = User.objects.get(email=email)
            verification_code = EmailVerificationCode.objects.get(user=user)

            if verification_code.code != code:
                raise serializers.ValidationError({"message": "კოდი არასწორია"})
            
            if verification_code.is_expired():
                raise serializers.ValidationError({"message": "კოდი ვადაგასულია"})
        except (User.DoesNotExist, EmailVerificationCode.DoesNotExist):
            raise serializers.ValidationError({"message": "ვერ მოიძებნა მომხმარებელი ან მასთან დაკავშირებული კოდი"})
        
        attrs['user'] = user
        return attrs