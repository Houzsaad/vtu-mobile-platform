from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Announcement


class AnnouncementListView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        items = Announcement.current().values("id", "title", "message", "level", "created_at")[:5]
        return Response(list(items))
    
# Create your views here.
