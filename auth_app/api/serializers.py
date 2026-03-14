from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for incoming registration request.
    """
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "confirmed_password"]
        read_only_fields = ["id"]
        extra_kwargs = {
            "email": {"required": True},
            "username": {"required": False}
        }

    def validate(self, attrs):
        """
        Check if passwords do match
        """
        if attrs["password"] != attrs["confirmed_password"]:
            raise serializers.ValidationError({"password": "Password do not match!"})
        return attrs
    
    def validate_email(self, value):
        """
        Check if email is already in use
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already in use. Choose a different one!")
        return value
    
    def create(self, validated_data):
        """
        Custom create method. Used to create a new user and hash the password.
        """
        email = validated_data["email"]
        password = validated_data["password"]
        return User.objects.create_user(username=email, email=email, 
                                        password=password, is_active=False)
    

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Login serializer. Validates the request send with email and password.
    If the request is valid, the view will return a set of JWT tokens.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "username" in self.fields:
            self.fields.pop("username")

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Email or password is wrong.")
        
        if not user.check_password(password):
            raise serializers.ValidationError("Email or password incorrect.")
        
        data = super().validate({"username": user.username, "password": password})
        return data
    

class PasswordResetSerializer(serializers.ModelSerializer):
    """
    Used to validate the entered email. If not found, a validation error will be raised.
    """
    class Meta:
        model = User
        fields = ["email"]

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email does not exist.")
        return value
    

class NewPasswordSerializer(serializers.Serializer):
    """
    Validates the equality of the two entered passwords.
    If not equal, a validation error will be raised.
    """
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"password": "Passwords do not match!"})
        return attrs