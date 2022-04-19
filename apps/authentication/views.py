from rest_framework import viewsets
from rest_framework.parsers import FileUploadParser
from .serializers import SignupSerializer, ImageSerializer
from .models import User
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


class UserViewSet(viewsets.GenericViewSet):
    serializer_class = SignupSerializer
    queryset = User.objects.all()
    permission_classes = []

    def list(self, request, queryset):
        """
        function to list all users
        """
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        """
        Function to create a user
        """
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ImageUploadView(viewsets.GenericViewSet):
    parser_classes = [FileUploadParser]
    serializer_class = ImageSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = self.serializer_class(data=request.data, instance=request.user)
        if serializer.is_valid():
            serializer.save(
                photo=request.data.get('photo')
            )
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
