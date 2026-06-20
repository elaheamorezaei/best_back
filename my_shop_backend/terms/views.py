from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from core.responses import success_response, error_response
from .models import Term, TermsMetadata, WalletTermsSection, TermAcceptance


class TermListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        meta = TermsMetadata.get()
        terms = Term.objects.filter(is_active=True)
        data = {
            'terms': [
                {
                    'id': str(term.id),
                    'question': term.question,
                    'answer': term.answer,
                    'order': term.order,
                }
                for term in terms
            ],
            'lastUpdated': meta.last_updated,
            'version': meta.version,
        }
        return success_response(data)


class TermDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, term_id):
        try:
            term = Term.objects.get(pk=term_id, is_active=True)
        except Term.DoesNotExist:
            return error_response('قانون مورد نظر یافت نشد', 404)

        meta = TermsMetadata.get()
        data = {
            'id': str(term.id),
            'question': term.question,
            'answer': term.answer,
            'order': term.order,
            'lastUpdated': meta.last_updated,
        }
        return success_response(data)


class TermsHeroView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        meta = TermsMetadata.get()
        data = {
            'title': meta.hero_title,
            'subtitle': meta.hero_subtitle,
            'lastUpdated': meta.last_updated,
        }
        return success_response(data)


class WalletTermsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        meta = TermsMetadata.get()
        sections = WalletTermsSection.objects.all()
        data = {
            'title': meta.wallet_title,
            'sections': [
                {
                    'id': section.id,
                    'title': section.title,
                    'content': section.content,
                }
                for section in sections
            ],
        }
        return success_response(data)


class TermAcceptView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        meta = TermsMetadata.get()
        acceptance = TermAcceptance.objects.create(
            user=request.user,
            term_version=meta.version,
        )
        return Response({
            'success': True,
            'message': 'قوانین با موفقیت پذیرفته شد',
            'data': {
                'acceptedVersion': acceptance.term_version,
                'acceptedAt': acceptance.accepted_at.isoformat().replace('+00:00', 'Z'),
            },
        })
