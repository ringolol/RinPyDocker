from django.urls import path, include
from rest_framework import routers, serializers, viewsets
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.response import Response

from . import views
from .models import Block, DiagFiles
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class BlockSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Block
        fields = ['name', 'inpN', 'outpN', 'pars', 'states']

@method_decorator(csrf_exempt, name='dispatch')
class BlockViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    queryset = Block.objects.all()
    serializer_class = BlockSerializer


class FilesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DiagFiles
        fields = ['user', 'name', 'ser']

@method_decorator(csrf_exempt, name='dispatch')
class FilesViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    serializer_class = FilesSerializer

    def get_queryset(self):
        print(self.request.user.username)
        return DiagFiles.objects.filter(user=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


router = routers.DefaultRouter()
router.register(r'blocks', BlockViewSet)
router.register(r'files', FilesViewSet, basename='files')

urlpatterns = [
    # path('', views.diagram, name='diagram'),
    path('api/', include(router.urls)),
]