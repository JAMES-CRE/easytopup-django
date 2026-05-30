from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser
import cloudinary.uploader
import os

class UploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]
    
    def post(self, request):
        files = request.FILES.getlist('photos')
        if not files:
            return Response({'error': 'No files provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        urls = []
        for file in files:
            try:
                upload_result = cloudinary.uploader.upload(
                    file,
                    folder='report_photos',
                    transformation=[{'width': 800, 'height': 600, 'crop': 'limit'}]
                )
                urls.append(upload_result['secure_url'])
            except Exception as e:
                print(f'Upload error: {e}')
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({'data': urls}, status=status.HTTP_200_OK)