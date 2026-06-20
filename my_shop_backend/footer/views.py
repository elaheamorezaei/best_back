from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from core.responses import success_response
from .models import (
    SocialLink, CustomerServiceLink, ProductLink,
    AboutUsLink, FeatureBox, PartnerLogo,
)
from .serializers import (
    SocialLinkSerializer, CustomerServiceLinkSerializer, ProductLinkSerializer,
    AboutUsLinkSerializer, FeatureBoxSerializer, PartnerLogoSerializer,
)


class FooterDataView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        ctx = {'request': request}
        data = {
            "social_links": SocialLinkSerializer(
                SocialLink.objects.all(), many=True, context=ctx
            ).data,
            "customer_services": CustomerServiceLinkSerializer(
                CustomerServiceLink.objects.all(), many=True, context=ctx
            ).data,
            "products_links": ProductLinkSerializer(
                ProductLink.objects.all(), many=True, context=ctx
            ).data,
            "about_us_links": AboutUsLinkSerializer(
                AboutUsLink.objects.all(), many=True, context=ctx
            ).data,
            "feature_boxes": FeatureBoxSerializer(
                FeatureBox.objects.all(), many=True, context=ctx
            ).data,
            "partner_logos": PartnerLogoSerializer(
                PartnerLogo.objects.all(), many=True, context=ctx
            ).data,
        }
        return success_response(data)
