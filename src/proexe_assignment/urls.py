
from django.urls import include, path
from rest_framework import routers
from dynamic_tables.views import TableViewSet

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

router = routers.DefaultRouter()
router.register(r'table', TableViewSet, 'table')

urlpatterns = [
    path('api/', include(router.urls)),
]


schema_view = get_schema_view(
    openapi.Info(
        title="Django Dynamic Tables API",
        default_version='v1',
        description="""
        This projects showcases a basic use of the python type function to generate django models on the fly and, Django Schema Editor to create db tables and migrations on runtime. Was implemented as a recruitment tasks. 

        **Endpoints**

        - [/swagger](/swagger): live testing playground
        - [/](/): api documentation
        - [/api](/api): api endpoints
        """,
        license=openapi.License(name="BSD License"),


    ),
    public=True,
)

urlpatterns += [
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0),
         name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger',
                                         cache_timeout=0), name='schema-swagger-ui'),
    path('', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
