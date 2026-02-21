from django.contrib.auth.models import User

from rest_framework import serializers


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