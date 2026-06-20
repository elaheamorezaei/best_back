from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from core.responses import success_response, build_absolute_image_url
from products.models import Category
from .models import HeaderItem


def _build_category_node(category, request):
    return {
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
        "icon": category.icon,
        "image": build_absolute_image_url(request, category.image),
        "link": f"/category/{category.slug}",
        "children": [
            _build_category_node(child, request)
            for child in category.children.all()
        ],
    }


class MegaMenuView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        top_level = Category.objects.filter(parent__isnull=True).prefetch_related('children')
        header_items = HeaderItem.objects.filter(is_active=True)

        mega_menu = {}
        categories_list = []

        for cat in top_level:
            node = _build_category_node(cat, request)
            mega_menu[cat.slug] = node
            categories_list.append({
                "id": cat.id,
                "name": cat.name,
                "slug": cat.slug,
                "icon": cat.icon,
            })

        header_items_data = [
            {"id": item.id, "name": item.name, "link": item.link, "icon": item.icon}
            for item in header_items
        ]

        data = {
            "mega_menu": mega_menu,
            "categories_list": categories_list,
            "header_items": header_items_data,
        }
        return success_response(data)
