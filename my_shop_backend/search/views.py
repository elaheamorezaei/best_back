from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.responses import success_response, error_response
from .models import TrendingSearch
from products.models import Product


class TrendingSearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        searches = TrendingSearch.objects.filter(is_active=True)
        data = [{"title": s.title, "link": s.link} for s in searches]
        return success_response(data)


class AutocompleteView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        q = request.query_params.get('q', '').strip()
        if len(q) < 2:
            return error_response("Search term must be at least 2 characters", 400)

        products = (
            Product.objects
            .filter(name__icontains=q)
            .select_related('category')[:10]
        )
        data = [
            {
                "name": p.name,
                "category": p.category.name,
                "link": f"/product/{p.id}",
            }
            for p in products
        ]
        return Response({"success": True, "query": q, "data": data})
