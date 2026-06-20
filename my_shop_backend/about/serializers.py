from rest_framework import serializers
from core.responses import build_absolute_image_url
from .models import (
    AboutSlider, AboutStoryParagraph, AboutWhyUsItem,
    AboutBranchSection, AboutBranch, AboutDescriptionSection,
    AboutTeamMember, AboutStat,
)


class AboutSliderSerializer(serializers.ModelSerializer):
    src = serializers.SerializerMethodField()

    class Meta:
        model = AboutSlider
        fields = ['src', 'alt']

    def get_src(self, obj):
        return build_absolute_image_url(self.context.get('request'), obj.image)


class AboutStorySerializer(serializers.Serializer):
    paragraphs = serializers.SerializerMethodField()

    def get_paragraphs(self, paragraphs_qs):
        return [p.text for p in paragraphs_qs]


class AboutWhyUsItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutWhyUsItem
        fields = ['id', 'name', 'icon']


class AboutBranchSerializer(serializers.ModelSerializer):
    workingHours = serializers.CharField(source='working_hours')

    class Meta:
        model = AboutBranch
        fields = ['id', 'name', 'address', 'phone', 'workingHours']


class AboutBranchSectionSerializer(serializers.ModelSerializer):
    src = serializers.SerializerMethodField()
    branchList = serializers.SerializerMethodField()

    class Meta:
        model = AboutBranchSection
        fields = ['src', 'alt', 'branchList']

    def get_src(self, obj):
        return build_absolute_image_url(self.context.get('request'), obj.image)

    def get_branchList(self, obj):
        branches = AboutBranch.objects.all()
        return AboutBranchSerializer(branches, many=True).data


class AboutDescriptionSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutDescriptionSection
        fields = ['id', 'title', 'content']


class AboutTeamMemberSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = AboutTeamMember
        fields = ['id', 'name', 'role', 'avatar', 'bio']

    def get_avatar(self, obj):
        return build_absolute_image_url(self.context.get('request'), obj.avatar)


class AboutStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutStat
        fields = ['label', 'value']
