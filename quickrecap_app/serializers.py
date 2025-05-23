from rest_framework import generics, status
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import authenticate

from .models import *
from .serializers import *

from django.contrib.auth import get_user_model
from django.contrib.auth import password_validation
from django.utils.translation import gettext_lazy as _

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['password', 'email', 'nombres', 'apellidos', 'celular', 'genero']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            nombres=validated_data['nombres'],
            apellidos=validated_data['apellidos'],
            celular=validated_data.get('celular', None),
            genero=validated_data.get('genero', None),
            #fecha_nacimiento=validated_data.get('fecha_nacimiento', None),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError(_("Invalid login credentials."))

            # Verificar si la contraseña es correcta
            if not user.check_password(password):
                raise serializers.ValidationError(_("Invalid login credentials."))

            # Si todo está bien, retornamos el usuario
            data['user'] = user
        else:
            raise serializers.ValidationError(_("Must include 'email' and 'password'."))

        return data

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    
#----------- REPORTE ERROR SERIALIZER --------- #
class ReporteErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReporteError
        fields = ['nombre', 'descripcion']

class ReportErrorListSerializer(serializers.ModelSerializer):
    class Meta: 
        model = ReporteError
        fields = '__all__'
        
#----------- USER SERIALIZER --------- #
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nombres', 'apellidos', 'celular', 'genero', 'fecha_nacimiento', 'profile_image']
        
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nombres', 'apellidos', 'celular', 'genero', 'fecha_nacimiento', 'profile_image', 'puntos']

class UserUpdatePointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['puntos']

#----------- FILE SERIALIZER --------- #
class FileSerializer(serializers.ModelSerializer):
    class Meta: 
        model = File
        fields = '__all__'

#----------- ACTIVIDAD SERIALIZER --------- #
class ActivityListSerializer(serializers.ModelSerializer):
    favourite = serializers.SerializerMethodField()

    class Meta:
        model = Actividad
        fields = [
            'id',
            'tipo_actividad',
            'tiempo_por_pregunta',
            'numero_preguntas',
            'veces_jugado',
            'puntuacion_maxima',
            'completado',
            'privado',
            'nombre',
            'usuario',
            'flashcard_id',
            'favourite'
        ]
        depth = 1

    def get_favourite(self, obj):
        user_id = self.context.get('user_id')
        print("User ID:", user_id)
        return Favoritos.objects.filter(
            user_id=user_id,
            activity_id=obj.id
        ).exists()

class ActivityCreateSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Actividad
        fields = ['tipo_actividad', 'tiempo_por_pregunta', 'numero_preguntas', 'nombre', 'usuario', 'flashcard_id']

#----------- FAVORITOS SERIALIZER --------- #
class FavoritoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favoritos
        fields = '__all__'
        
#----------- RATED SERIALIZER --------- #
class RatedListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rated
        fields = '__all__'

#----------- HISTORIAL SERIALIZER --------- #  
class HistorialListSerializer(serializers.ModelSerializer):
    nombre_actividad = serializers.CharField(source='activity.nombre')
    tipo_actividad = serializers.CharField(source='activity.tipo_actividad')
    
    class Meta:
        model = Historial
        fields = ['id', 'nombre_actividad', 'tipo_actividad', 'numero_preguntas', 'respuestas_correctas', 
                 'fecha', 'activity', 'user']
        depth=1

#----------- HISTORIAL SERIALIZER --------- #  
class HistorialCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Historial
        fields = '__all__'