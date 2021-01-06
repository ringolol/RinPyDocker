from rest_framework.response import Response
from rest_framework.decorators import api_view

from .services.diagram_parser import parse_diagram


@api_view(['POST'])
def diagram_parser_view(request):
    return Response({
        # "output": ,
        "output": parse_diagram(request.data),
    })