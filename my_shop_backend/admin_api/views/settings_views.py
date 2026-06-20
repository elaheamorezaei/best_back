import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from admin_api.permissions import IsAdminUser
from admin_api.models import SiteSettings, ThemeSettings, SEOPageSettings
from core.responses import build_absolute_image_url


class AdminSiteSettingsView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        s = SiteSettings.get()
        return Response({
            'siteName': s.site_name,
            'siteDescription': s.site_description,
            'siteKeywords': s.site_keywords or [],
            'logo': build_absolute_image_url(request, s.logo),
            'favicon': build_absolute_image_url(request, s.favicon),
            'email': s.email,
            'phone': s.phone,
            'address': s.address,
            'instagram': s.instagram,
            'telegram': s.telegram,
            'whatsapp': s.whatsapp,
            'googleAnalyticsId': s.google_analytics_id,
            'googleTagManagerId': s.google_tag_manager_id,
            'robotsTxt': s.robots_txt,
            'maintenanceMode': s.maintenance_mode,
        })

    def patch(self, request):
        s = SiteSettings.get()
        data = request.data
        update_fields = []

        str_map = [
            ('siteName', 'site_name'), ('siteDescription', 'site_description'),
            ('email', 'email'), ('phone', 'phone'), ('address', 'address'),
            ('instagram', 'instagram'), ('telegram', 'telegram'), ('whatsapp', 'whatsapp'),
            ('googleAnalyticsId', 'google_analytics_id'), ('googleTagManagerId', 'google_tag_manager_id'),
            ('robotsTxt', 'robots_txt'),
        ]
        for api_key, model_field in str_map:
            if api_key in data:
                setattr(s, model_field, data[api_key])
                update_fields.append(model_field)

        if 'siteKeywords' in data:
            kw = data['siteKeywords']
            if isinstance(kw, str):
                try:
                    kw = json.loads(kw)
                except Exception:
                    kw = []
            s.site_keywords = kw
            update_fields.append('site_keywords')

        if 'maintenanceMode' in data:
            s.maintenance_mode = str(data['maintenanceMode']).lower() not in ('false', '0')
            update_fields.append('maintenance_mode')

        if 'logo' in request.FILES:
            s.logo = request.FILES['logo']
            update_fields.append('logo')

        if 'favicon' in request.FILES:
            s.favicon = request.FILES['favicon']
            update_fields.append('favicon')

        if update_fields:
            s.save(update_fields=update_fields)

        s.refresh_from_db()
        return self.get(request)


class AdminThemeSettingsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        t = ThemeSettings.get()
        return Response({
            'primary': t.primary,
            'secondary': t.secondary,
            'accent': t.accent,
            'neutral': t.neutral,
            'base': t.base,
            'info': t.info,
            'success': t.success,
            'warning': t.warning,
            'error': t.error,
            'radius': t.radius,
            'fontFamily': t.font_family,
            'mode': t.mode,
        })

    def put(self, request):
        t = ThemeSettings.get()
        data = request.data
        field_map = [
            ('primary', 'primary'), ('secondary', 'secondary'), ('accent', 'accent'),
            ('neutral', 'neutral'), ('base', 'base'), ('info', 'info'),
            ('success', 'success'), ('warning', 'warning'), ('error', 'error'),
            ('radius', 'radius'), ('fontFamily', 'font_family'), ('mode', 'mode'),
        ]
        update_fields = []
        for api_key, model_field in field_map:
            if api_key in data:
                setattr(t, model_field, data[api_key])
                update_fields.append(model_field)
        if update_fields:
            t.save(update_fields=update_fields)
        return self.get(request)


class AdminSEOSettingsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        pages = SEOPageSettings.objects.all()
        return Response([
            {
                'page': p.page,
                'path': p.path,
                'metaTitle': p.meta_title,
                'metaDescription': p.meta_description,
                'keywords': p.keywords or [],
                'ogImage': p.og_image or None,
                'noIndex': p.no_index,
            }
            for p in pages
        ])

    def post(self, request):
        data = request.data
        path = data.get('path', '').strip()
        if not path:
            return Response({'error': {'message': 'path الزامی است', 'code': 'MISSING_PATH'}}, status=400)

        keywords = data.get('keywords', [])
        if isinstance(keywords, str):
            try:
                keywords = json.loads(keywords)
            except Exception:
                keywords = []

        page_obj, _ = SEOPageSettings.objects.update_or_create(
            path=path,
            defaults={
                'page': data.get('page', path),
                'meta_title': data.get('metaTitle', ''),
                'meta_description': data.get('metaDescription', ''),
                'keywords': keywords,
                'og_image': data.get('ogImage', ''),
                'no_index': bool(data.get('noIndex', False)),
            }
        )

        return Response({
            'page': page_obj.page,
            'path': page_obj.path,
            'metaTitle': page_obj.meta_title,
            'metaDescription': page_obj.meta_description,
            'keywords': page_obj.keywords or [],
            'ogImage': page_obj.og_image or None,
            'noIndex': page_obj.no_index,
        })
