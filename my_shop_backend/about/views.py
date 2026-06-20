from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from core.responses import success_response
from .models import (
    AboutSlider, AboutStoryParagraph, AboutWhyUsItem,
    AboutBranchSection, AboutBranch, AboutDescriptionSection,
    AboutTeamMember, AboutStat,
)
from .serializers import (
    AboutSliderSerializer, AboutWhyUsItemSerializer,
    AboutBranchSectionSerializer, AboutBranchSerializer,
    AboutDescriptionSectionSerializer, AboutTeamMemberSerializer,
    AboutStatSerializer,
)


def _build_slider_data(request):
    slider = AboutSlider.objects.first()
    if not slider:
        return None
    return AboutSliderSerializer(slider, context={'request': request}).data


def _build_story_data():
    paragraphs = AboutStoryParagraph.objects.all()
    return {'paragraphs': [p.text for p in paragraphs]}


def _build_why_us_data():
    items = AboutWhyUsItem.objects.all()
    return {'items': AboutWhyUsItemSerializer(items, many=True).data}


def _build_branches_data(request):
    section = AboutBranchSection.objects.first()
    if not section:
        branches = AboutBranch.objects.all()
        return {
            'src': None,
            'alt': '',
            'branchList': AboutBranchSerializer(branches, many=True).data,
        }
    return AboutBranchSectionSerializer(section, context={'request': request}).data


def _build_description_data():
    sections = AboutDescriptionSection.objects.all()
    return {'sections': AboutDescriptionSectionSerializer(sections, many=True).data}


class AboutPageView(APIView):
    """GET /about — همه اطلاعات صفحه درباره ما در یک پاسخ"""
    permission_classes = [AllowAny]

    def get(self, request):
        data = {
            'slider': _build_slider_data(request),
            'story': _build_story_data(),
            'whyUs': _build_why_us_data()['items'],
            'branches': _build_branches_data(request),
            'description': _build_description_data(),
        }
        return success_response(data)


class AboutSliderView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return success_response(_build_slider_data(request))


class AboutStoryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return success_response(_build_story_data())


class AboutWhyUsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return success_response(_build_why_us_data())


class AboutBranchesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return success_response(_build_branches_data(request))


class AboutDescriptionView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return success_response(_build_description_data())


class AboutTeamView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        members = AboutTeamMember.objects.all()
        serializer = AboutTeamMemberSerializer(members, many=True, context={'request': request})
        return success_response({'members': serializer.data})


class AboutStatsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        stats = AboutStat.objects.all()
        serializer = AboutStatSerializer(stats, many=True)
        return success_response({'stats': serializer.data})
