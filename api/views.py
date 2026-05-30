from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import cloudinary
import cloudinary.uploader
from django.conf import settings

# Configure Cloudinary (add this at the top)
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_photos(request):
    """
    Upload multiple photos for stations or reports
    Matches Flutter: uploadPhotos() sending field name 'photos'
    """
    try:
        print("=== UPLOAD PHOTOS ===")
        print(f"Cloud name: {settings.CLOUDINARY_CLOUD_NAME}")
        print(f"API Key exists: {settings.CLOUDINARY_API_KEY is not None}")
        print(f"Files in request: {request.FILES.keys()}")

        # Check for 'photos' field (matches Flutter)
        if 'photos' not in request.FILES:
            return Response(
                {'error': 'No photos provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        uploaded_urls = []
        files = request.FILES.getlist('photos')
        print(f"Number of files: {len(files)}")

        for photo in files:
            print(f"Uploading: {photo.name}")

            upload_result = cloudinary.uploader.upload(
                photo,
                folder='easy_top_up',
                allowed_formats=['jpg', 'jpeg', 'png', 'webp'],
                transformation={'width': 800, 'height': 600, 'crop': 'limit'}
            )
            uploaded_urls.append(upload_result['secure_url'])
            print(f"Uploaded: {upload_result['secure_url']}")

        return Response({
            'success': True,
            'data': uploaded_urls
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Error: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_profile_photo(request):
    """
    Upload single profile photo
    Matches Flutter: uploadProfilePhoto() sending field name 'photo'
    """
    try:
        print("=== UPLOAD PROFILE PHOTO ===")
        
        if 'photo' not in request.FILES:
            return Response(
                {'error': 'No photo provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        photo = request.FILES['photo']
        print(f"Photo: {photo.name}")

        upload_result = cloudinary.uploader.upload(
            photo,
            folder='profile_photos',
            allowed_formats=['jpg', 'jpeg', 'png', 'webp'],
            transformation={'width': 300, 'height': 300, 'crop': 'limit'}
        )

        print(f"Uploaded URL: {upload_result['secure_url']}")

        return Response({
            'success': True,
            'data': upload_result['secure_url']
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Error: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )