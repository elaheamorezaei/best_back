from django.urls import path
from admin_api.views.auth import AdminLoginView, AdminTokenRefreshView, AdminLogoutView
from admin_api.views.dashboard import (
    DashboardStatsView, DashboardRevenueView,
    DashboardTopProductsView, DashboardRecentOrdersView,
)
from admin_api.views.products import (
    AdminProductListView, AdminProductDetailView,
    AdminProductToggleActiveView, AdminProductToggleFeaturedView,
    AdminProductBulkDeleteView,
)
from admin_api.views.categories import (
    AdminCategoryListView, AdminCategoryAllView,
    AdminCategoryDetailView, AdminCategoryReorderView,
)
from admin_api.views.orders import (
    AdminOrderListView, AdminOrderDetailView, AdminOrderNoteView,
    AdminOrderCancelView, AdminOrderRefundView,
)
from admin_api.views.users import (
    AdminUserListView, AdminUserDetailView,
    AdminUserToggleActiveView, AdminUserWalletView,
)
from admin_api.views.blog import (
    AdminBlogListView, AdminBlogDetailView, AdminBlogTogglePublishView,
)
from admin_api.views.banners import (
    AdminBannerListView, AdminBannerDetailView, AdminBannerReorderView,
)
from admin_api.views.sliders import (
    AdminSliderListView, AdminSliderDetailView, AdminSliderReorderView,
)
from admin_api.views.faq import (
    AdminFAQCategoryListView, AdminFAQCategoryDetailView,
    AdminFAQListView, AdminFAQDetailView, AdminFAQReorderView,
)
from admin_api.views.discounts import (
    AdminDiscountListView, AdminDiscountDetailView, AdminDiscountToggleActiveView,
)
from admin_api.views.messages import (
    AdminMessageListView, AdminMessageDetailView, AdminMessageReplyView,
    AdminMessageMarkReadView, AdminMessageBulkDeleteView,
)
from admin_api.views.reviews_admin import (
    AdminReviewListView, AdminReviewDetailView,
    AdminReviewApproveView, AdminReviewRejectView, AdminReviewBulkApproveView,
)
from admin_api.views.settings_views import (
    AdminSiteSettingsView, AdminThemeSettingsView, AdminSEOSettingsView,
)
from admin_api.views.reports import (
    AdminReportSalesView, AdminReportProductsView, AdminReportOrdersView,
)
from admin_api.views.upload import AdminUploadView

urlpatterns = [
    # Auth
    path('admin/auth/login/', AdminLoginView.as_view()),
    path('admin/auth/refresh/', AdminTokenRefreshView.as_view()),
    path('admin/auth/logout/', AdminLogoutView.as_view()),

    # Dashboard
    path('admin/dashboard/stats/', DashboardStatsView.as_view()),
    path('admin/dashboard/revenue/', DashboardRevenueView.as_view()),
    path('admin/dashboard/top-products/', DashboardTopProductsView.as_view()),
    path('admin/dashboard/recent-orders/', DashboardRecentOrdersView.as_view()),

    # Products
    path('admin/products/', AdminProductListView.as_view()),
    path('admin/products/bulk-delete/', AdminProductBulkDeleteView.as_view()),
    path('admin/products/<int:pk>/', AdminProductDetailView.as_view()),
    path('admin/products/<int:pk>/toggle-active/', AdminProductToggleActiveView.as_view()),
    path('admin/products/<int:pk>/toggle-featured/', AdminProductToggleFeaturedView.as_view()),

    # Categories
    path('admin/categories/', AdminCategoryListView.as_view()),
    path('admin/categories/all/', AdminCategoryAllView.as_view()),
    path('admin/categories/reorder/', AdminCategoryReorderView.as_view()),
    path('admin/categories/<int:pk>/', AdminCategoryDetailView.as_view()),

    # Orders
    path('admin/orders/', AdminOrderListView.as_view()),
    path('admin/orders/<int:pk>/', AdminOrderDetailView.as_view()),
    path('admin/orders/<int:pk>/note/', AdminOrderNoteView.as_view()),
    path('admin/orders/<int:pk>/cancel/', AdminOrderCancelView.as_view()),
    path('admin/orders/<int:pk>/refund/', AdminOrderRefundView.as_view()),

    # Users
    path('admin/users/', AdminUserListView.as_view()),
    path('admin/users/<int:pk>/', AdminUserDetailView.as_view()),
    path('admin/users/<int:pk>/toggle-active/', AdminUserToggleActiveView.as_view()),
    path('admin/users/<int:pk>/wallet/', AdminUserWalletView.as_view()),

    # Blog
    path('admin/blog/', AdminBlogListView.as_view()),
    path('admin/blog/<int:pk>/', AdminBlogDetailView.as_view()),
    path('admin/blog/<int:pk>/toggle-publish/', AdminBlogTogglePublishView.as_view()),

    # Banners
    path('admin/banners/', AdminBannerListView.as_view()),
    path('admin/banners/reorder/', AdminBannerReorderView.as_view()),
    path('admin/banners/<int:pk>/', AdminBannerDetailView.as_view()),

    # Sliders
    path('admin/sliders/', AdminSliderListView.as_view()),
    path('admin/sliders/reorder/', AdminSliderReorderView.as_view()),
    path('admin/sliders/<int:pk>/', AdminSliderDetailView.as_view()),

    # FAQ Categories
    path('admin/faq/categories/', AdminFAQCategoryListView.as_view()),
    path('admin/faq/categories/<int:pk>/', AdminFAQCategoryDetailView.as_view()),
    # FAQ
    path('admin/faq/', AdminFAQListView.as_view()),
    path('admin/faq/reorder/', AdminFAQReorderView.as_view()),
    path('admin/faq/<int:pk>/', AdminFAQDetailView.as_view()),

    # Discounts
    path('admin/discounts/', AdminDiscountListView.as_view()),
    path('admin/discounts/<int:pk>/', AdminDiscountDetailView.as_view()),
    path('admin/discounts/<int:pk>/toggle-active/', AdminDiscountToggleActiveView.as_view()),

    # Messages (Contact Tickets)
    path('admin/messages/', AdminMessageListView.as_view()),
    path('admin/messages/bulk-delete/', AdminMessageBulkDeleteView.as_view()),
    path('admin/messages/<int:pk>/', AdminMessageDetailView.as_view()),
    path('admin/messages/<int:pk>/reply/', AdminMessageReplyView.as_view()),
    path('admin/messages/<int:pk>/mark-read/', AdminMessageMarkReadView.as_view()),

    # Reviews
    path('admin/reviews/', AdminReviewListView.as_view()),
    path('admin/reviews/bulk-approve/', AdminReviewBulkApproveView.as_view()),
    path('admin/reviews/<int:pk>/', AdminReviewDetailView.as_view()),
    path('admin/reviews/<int:pk>/approve/', AdminReviewApproveView.as_view()),
    path('admin/reviews/<int:pk>/reject/', AdminReviewRejectView.as_view()),

    # Settings
    path('admin/settings/site/', AdminSiteSettingsView.as_view()),
    path('admin/settings/theme/', AdminThemeSettingsView.as_view()),
    path('admin/settings/seo/', AdminSEOSettingsView.as_view()),

    # Reports
    path('admin/reports/sales/', AdminReportSalesView.as_view()),
    path('admin/reports/products/', AdminReportProductsView.as_view()),
    path('admin/reports/orders/', AdminReportOrdersView.as_view()),

    # Upload
    path('admin/upload/', AdminUploadView.as_view()),
]
