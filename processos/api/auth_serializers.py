from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from processos.models_auth import UserProfile, AccessApproval


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)
    nome_completo = serializers.CharField(max_length=255)
    cargo = serializers.CharField(max_length=255, required=False, default='', allow_blank=True)
    is_decipex = serializers.BooleanField(required=False, default=False)
    area_codigo = serializers.CharField(max_length=50, required=False, default='', allow_blank=True)
    setor_trabalho = serializers.CharField(max_length=255, required=False, default='', allow_blank=True)

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Este email ja esta cadastrado.')
        return email

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'As senhas nao conferem.'})

        is_decipex = data.get('is_decipex', False)
        area_codigo = data.get('area_codigo', '').strip()
        setor_trabalho = data.get('setor_trabalho', '').strip()

        if is_decipex and not area_codigo:
            raise serializers.ValidationError({'area_codigo': 'Selecione a area da Decipex.'})
        if not is_decipex and not setor_trabalho:
            raise serializers.ValidationError({'setor_trabalho': 'Informe o setor de trabalho.'})

        return data


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        return value.strip().lower()


class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    is_superuser = serializers.BooleanField(source='user.is_superuser', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'email', 'username', 'is_superuser',
            'profile_type', 'email_verified', 'access_status',
            'role',
            'nome_completo', 'cargo',
            'orgao', 'area',
            'created_at',
        ]
        read_only_fields = fields


class PendingUserSerializer(serializers.ModelSerializer):
    """Serializer para listagem de usuarios pendentes (painel admin)."""
    email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    approvals_count = serializers.SerializerMethodField()
    rejections_count = serializers.SerializerMethodField()
    votes = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id', 'email', 'username',
            'profile_type', 'access_status', 'email_verified',
            'nome_completo', 'cargo',
            'created_at',
            'approvals_count', 'rejections_count', 'votes',
        ]

    def get_approvals_count(self, obj):
        return obj.approvals.filter(vote='approve', admin__is_active=True).count()

    def get_rejections_count(self, obj):
        return obj.approvals.filter(vote='reject', admin__is_active=True).count()

    def get_votes(self, obj):
        return [
            {
                'admin_email': v.admin.email if v.admin else None,
                'vote': v.vote,
                'justificativa': v.justificativa,
                'voted_at': v.voted_at.isoformat(),
            }
            for v in obj.approvals.filter(admin__is_active=True).select_related('admin')
        ]


class VoteSerializer(serializers.Serializer):
    vote = serializers.ChoiceField(choices=['approve', 'reject'])
    justificativa = serializers.CharField(required=False, default='')


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return value.strip().lower()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=6)

    def validate_password(self, value):
        validate_password(value)
        return value
