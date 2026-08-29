import uuid

from django.conf import settings
from rest_framework import generics, parsers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import UploadedFile
from .serializers import UploadedFileSerializer
from .validators import validate_mime_type, validate_upload_size

MIME_TO_TYPE = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "document",
    "image/jpeg": "image",
    "image/png": "image",
    "image/webp": "image",
    "audio/mpeg": "audio",
    "audio/wav": "audio",
    "text/plain": "document",
    "text/markdown": "document",
}


class FileUploadView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UploadedFileSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request, *args, **kwargs):
        uploaded = request.FILES.get("file")
        if not uploaded:
            return Response({"detail": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        max_size = (
            settings.MAX_UPLOAD_SIZE_PRO
            if request.user.plan == "pro"
            else settings.MAX_UPLOAD_SIZE_FREE
        )
        try:
            validate_upload_size(uploaded, max_size)
            validate_mime_type(uploaded)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        mime = uploaded.content_type or "application/octet-stream"
        stored_name = f"{uuid.uuid4()}_{uploaded.name}"

        record = UploadedFile.objects.create(
            user=request.user,
            original_name=uploaded.name,
            stored_name=stored_name,
            file=uploaded,
            file_type=MIME_TO_TYPE.get(mime, "other"),
            mime_type=mime,
            size_bytes=uploaded.size,
        )

        return Response(
            UploadedFileSerializer(record, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class FileListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UploadedFileSerializer

    def get_queryset(self):
        return UploadedFile.objects.filter(user=self.request.user)


class FileDetailView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UploadedFileSerializer

    def get_queryset(self):
        return UploadedFile.objects.filter(user=self.request.user)
