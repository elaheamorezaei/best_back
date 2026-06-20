import math
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.responses import data_response, error_detail_response, success_response, error_response
from core.responses import build_absolute_image_url
from core.utils import to_persian_date
from products.models import Product
from .models import Wishlist, StockNotification


class WishlistToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return error_detail_response(404, "محصول یافت نشد", http_status=404)

        obj, created = Wishlist.objects.get_or_create(user=request.user, product=product)
        if not created:
            obj.delete()
            return data_response({'isInWishlist': False}, message="از علاقه‌مندی‌ها حذف شد")

        return data_response({'isInWishlist': True}, message="به علاقه‌مندی‌ها اضافه شد")


class StockNotifyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return error_detail_response(404, "محصول یافت نشد", http_status=404)

        if product.stock > 0:
            return error_detail_response(400, "محصول در انبار موجود است", field="product_id")

        obj, created = StockNotification.objects.get_or_create(
            user=request.user, product=product
        )
        if not created:
            obj.delete()
            return data_response({'isNotifyRequested': False}, message="اعلان موجودی لغو شد")

        return data_response({'isNotifyRequested': True}, message="اعلان موجودی فعال شد")


# ---------------------------------------------------------------------------
# Profile favorites: GET/POST /profile/favorites, DELETE /profile/favorites/{id}
# ---------------------------------------------------------------------------

class FavoritesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = (
            Wishlist.objects
            .filter(user=request.user)
            .select_related('product')
            .prefetch_related('product__images')
            .order_by('-created_at')
        )

        try:
            page = max(1, int(request.query_params.get('page', 1)))
        except (ValueError, TypeError):
            page = 1
        try:
            limit = max(1, min(50, int(request.query_params.get('limit', 12))))
        except (ValueError, TypeError):
            limit = 12

        total = qs.count()
        total_pages = math.ceil(total / limit) if total else 1
        items = list(qs[(page - 1) * limit: page * limit])

        favorites = []
        for wl in items:
            product = wl.product
            first_img = product.images.first()
            image_url = None
            if first_img:
                image_url = build_absolute_image_url(request, first_img.image)
            elif product.image:
                image_url = build_absolute_image_url(request, product.image)

            old_price = int(product.price) if product.off else None
            discount = product.off if product.off else None

            favorites.append({
                'id': wl.id,
                'productId': product.id,
                'image': image_url,
                'name': product.name,
                'price': product.final_price,
                'oldPrice': old_price,
                'discount': discount,
                'inStock': product.in_stock,
                'addedAt': to_persian_date(wl.created_at),
            })

        return success_response({
            'favorites': favorites,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'totalPages': total_pages,
            },
        })

    def post(self, request):
        product_id = request.data.get('productId')
        if not product_id:
            return Response({'success': False, 'message': 'productId الزامی است'}, status=400)

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return error_response("محصول یافت نشد", status=404)

        if Wishlist.objects.filter(user=request.user, product=product).exists():
            return Response({
                'success': False,
                'message': 'این محصول قبلاً به علاقه‌مندی‌ها اضافه شده است',
            }, status=409)

        Wishlist.objects.create(user=request.user, product=product)
        return Response({'success': True, 'message': 'به علاقه‌مندی‌ها اضافه شد'}, status=201)


class FavoriteDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, favorite_id):
        try:
            wl = Wishlist.objects.get(pk=favorite_id, user=request.user)
        except Wishlist.DoesNotExist:
            return error_response("مورد یافت نشد", status=404)
        wl.delete()
        return Response({'success': True, 'message': 'از علاقه‌مندی‌ها حذف شد'})
