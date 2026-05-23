from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone

from .models import Doctor
from .serializers import DoctorSerializer, DoctorCreateSerializer
from users.permissions import IsAdmin, IsDoctor, IsPatient
from appointments.serializers import AppointmentSerializer


# ──────────────────────────────────────────────────────────────
# PUBLIC ENDPOINTS  (no auth needed)
# ──────────────────────────────────────────────────────────────

class PublicDoctorListView(generics.ListAPIView):
    """GET /api/doctors/  — list active doctors (public)"""
    permission_classes = [AllowAny]
    serializer_class = DoctorSerializer

    def get_queryset(self): 
        qs = Doctor.objects.filter(status='active')
        specialty = self.request.query_params.get('specialty')
        body_part = self.request.query_params.get('body_part')
        search = self.request.query_params.get('search')
        if specialty:
            qs = qs.filter(specialty__icontains=specialty)
        if body_part:
            qs = qs.filter(body_part__icontains=body_part)
        if search:
            qs = qs.filter(name__icontains=search)
        return qs


class PublicDoctorDetailView(generics.RetrieveAPIView):
    """GET /api/doctors/<pk>/  — doctor detail (public)"""
    permission_classes = [AllowAny]
    queryset = Doctor.objects.filter(status='active')
    serializer_class = DoctorSerializer

    def get_serializer_context(self):
        return {'request': self.request}


# ──────────────────────────────────────────────────────────────
# DOCTOR — own profile CRUD
# ──────────────────────────────────────────────────────────────

class DoctorProfileView(APIView):
    """GET / PUT  /api/doctors/my-profile/  — doctor manages own profile"""
    permission_classes = [IsDoctor]

    def get(self, request):
        try:
            doctor = Doctor.objects.get(user=request.user)
            return Response(DoctorSerializer(doctor, context={'request': request}).data)
        except Doctor.DoesNotExist:
            return Response({"error": "Doctor profile not found."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        try:
            doctor = Doctor.objects.get(user=request.user)
        except Doctor.DoesNotExist:
            return Response({"error": "Doctor profile not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = DoctorCreateSerializer(doctor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated.", "doctor": DoctorSerializer(doctor, context={'request': request}).data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────────────────────────
# ADMIN — full CRUD on doctors
# ──────────────────────────────────────────────────────────────

class AdminDoctorListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/admin/doctors/  — list all doctors
    POST /api/admin/doctors/  — create a doctor
    """
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAdmin]

    def create(self, request, *args, **kwargs):
        serializer = DoctorCreateSerializer(data=request.data)
        if serializer.is_valid():
            doctor = serializer.save()
            return Response(
                {"message": "Doctor created.", "doctor": DoctorSerializer(doctor).data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminDoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/admin/doctors/<pk>/
    PUT    /api/admin/doctors/<pk>/
    DELETE /api/admin/doctors/<pk>/
    """
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAdmin]

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        doctor = self.get_object()
        doctor.delete()
        return Response({"message": "Doctor deleted."}, status=status.HTTP_204_NO_CONTENT)


class DoctorLikeToggleView(APIView):
    """POST /api/doctors/<pk>/like/ and DELETE /api/doctors/<pk>/like/"""
    permission_classes = [IsAuthenticated, IsPatient]

    def post(self, request, pk):
        doctor = get_object_or_404(Doctor, pk=pk, status='active')
        doctor.liked_by.add(request.user)
        return Response({
            "message": "Doctor liked.",
            "likes_count": doctor.liked_by.count(),
            "liked_by_user": True,
        })

    def delete(self, request, pk):
        doctor = get_object_or_404(Doctor, pk=pk, status='active')
        doctor.liked_by.remove(request.user)
        return Response({
            "message": "Doctor unliked.",
            "likes_count": doctor.liked_by.count(),
            "liked_by_user": False,
        })


class DoctorLikesView(APIView):
    """GET /api/doctors/<pk>/likes/"""
    permission_classes = [AllowAny]

    def get(self, request, pk):
        doctor = get_object_or_404(Doctor, pk=pk, status='active')
        return Response({
            "doctor_id": doctor.pk,
            "likes_count": doctor.liked_by.count(),
        })


class AdminDoctorStatusView(APIView):
    """PATCH /api/admin/doctors/<pk>/status/"""
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        try:
            doctor = Doctor.objects.get(pk=pk)
        except Doctor.DoesNotExist:
            return Response({"error": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND)
        new_status = request.data.get('status')
        if new_status not in ['active', 'inactive']:
            return Response({"error": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)
        doctor.status = new_status
        doctor.save()
        return Response({"message": f"Doctor status set to {new_status}."})


class DoctorDashboardView(APIView):
    """GET /api/doctor/dashboard/ — personalized dashboard for doctors"""
    permission_classes = [IsDoctor]

    def get(self, request):
        try:
            doctor = Doctor.objects.get(user=request.user)
        except Doctor.DoesNotExist:
            return Response({"error": "Doctor profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Today's appointments
        today_appointments = doctor.get_today_appointments()
        today_stats = {
            "total": today_appointments.count(),
            "pending": today_appointments.filter(status='Pending').count(),
            "confirmed": today_appointments.filter(status='Confirmed').count(),
            "completed": today_appointments.filter(status='Completed').count(),
        }

        # Upcoming appointments (next 7 days)
        upcoming_appointments = doctor.get_upcoming_appointments(7)
        upcoming_stats = {
            "total": upcoming_appointments.count(),
            "next_appointment": AppointmentSerializer(upcoming_appointments.first()).data if upcoming_appointments.exists() else None,
        }

        # Monthly statistics
        monthly_stats = doctor.get_monthly_stats()

        # Overall statistics
        overall_stats = {
            "total_appointments": doctor.total_appointments,
            "completed_appointments": doctor.completed_appointments,
            "pending_appointments": doctor.pending_appointments,
            "likes_count": doctor.likes_count,
            "profile_completion": self._calculate_profile_completion(doctor),
        }

        return Response({
            "welcome_message": f"Good day, Dr. {doctor.name}!",
            "today_appointments": AppointmentSerializer(today_appointments, many=True).data,
            "today_stats": today_stats,
            "upcoming_stats": upcoming_stats,
            "monthly_stats": monthly_stats,
            "overall_stats": overall_stats,
        })

    def _calculate_profile_completion(self, doctor):
        """Calculate profile completion percentage"""
        fields = [
            doctor.name, doctor.specialty, doctor.experience,
            doctor.clinic_address, doctor.clinic_phone, doctor.about
        ]
        completed_fields = sum(1 for field in fields if field)
        return int((completed_fields / len(fields)) * 100)
