from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from categorization.serializers import (
    CategorizationRequestSerializer,
    CategorizationResponseSerializer,
)
from categorization.services.categorization_service import CategorizationService


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"status": "ok"}, status=status.HTTP_200_OK)


class CategorizationSuggestView(APIView):
    authentication_classes = []
    permission_classes = []
    service_class = CategorizationService

    def post(self, request):
        serializer = CategorizationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        suggestion = self.service_class().suggest(serializer.validated_data)
        response_serializer = CategorizationResponseSerializer(suggestion)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
