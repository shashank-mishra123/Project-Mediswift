from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Appointment
from .serializers import AppointmentSerializer, AppointmentCreateSerializer, AppointmentStatusSerializer
from users.permissions import IsAdmin, IsDoctor, IsPatient
from doctors.models import Doctor


# ──────────────────────────────────────────────────────────────
# PATIENT — book & view own appointments
# ──────────────────────────────────────────────────────────────

class BookAppointmentView(APIView):
    """POST /api/appointments/  — book an appointment with validation"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AppointmentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        doctor_id = serializer.validated_data['doctor_id']
        appointment_date = serializer.validated_data['appointment_date']
        appointment_time = serializer.validated_data['appointment_time']

        # Validate doctor exists and is active
        try:
            doctor = Doctor.objects.get(pk=doctor_id, status='active')
        except Doctor.DoesNotExist:
            return Response({"error": "Doctor not found or unavailable."}, status=status.HTTP_404_NOT_FOUND)

        # Check if slot is available
        if Appointment.objects.filter(
            doctor=doctor,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status__in=['Pending', 'Confirmed']
        ).exists():
            return Response({"error": "This time slot is already booked."}, status=400)

        # Check if patient already has an appointment with this doctor on the same day
        if Appointment.objects.filter(
            patient=request.user,
            doctor=doctor,
            appointment_date=appointment_date,
            status__in=['Pending', 'Confirmed']
        ).exists():
            return Response({"error": "You already have an appointment with this doctor on this date."}, status=400)

        # Check appointment date is not in the past
        from datetime import date
        if appointment_date < date.today():
            return Response({"error": "Cannot book appointments in the past."}, status=400)

        # Create appointment
        appointment = Appointment.objects.create(
            doctor=doctor,
            patient=request.user,
            patient_name=request.user.name,
            patient_mobile=getattr(request.user, 'phone', ''),
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            notes=serializer.validated_data.get('notes', '')
        )

        return Response(
            {"message": "Appointment booked successfully.", "appointment": AppointmentSerializer(appointment).data},
            status=status.HTTP_201_CREATED
        )


class MyAppointmentsView(generics.ListAPIView):
    """GET /api/appointments/my/  — patient sees own appointments"""
    permission_classes = [IsAuthenticated]
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        return Appointment.objects.filter(patient=self.request.user)


class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET / PUT / DELETE /api/appointments/<pk>/"""
    permission_classes = [IsAuthenticated]
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Appointment.objects.all()
        if user.role == 'doctor':
            return Appointment.objects.filter(doctor__user=user)
        return Appointment.objects.filter(patient=user)

    def destroy(self, request, *args, **kwargs):
        appointment = self.get_object()
        appointment.delete()
        return Response({"message": "Appointment deleted."}, status=status.HTTP_204_NO_CONTENT)


class CancelAppointmentView(APIView):
    """PATCH /api/appointments/<pk>/cancel/  — patient cancels own"""
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            appointment = Appointment.objects.get(pk=pk, patient=request.user)
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)
        if appointment.status in ['Completed', 'Cancelled']:
            return Response({"error": "Cannot cancel a completed or already cancelled appointment."}, status=400)
        appointment.status = 'Cancelled'
        appointment.save()
        return Response({"message": "Appointment cancelled."})


# ──────────────────────────────────────────────────────────────
# PUBLIC — check booked slots
# ──────────────────────────────────────────────────────────────

class BookedSlotsView(APIView):
    """GET /api/appointments/booked-slots/?doctor_id=&date=  — public"""
    permission_classes = [AllowAny]

    def get(self, request):
        doctor_id = request.query_params.get('doctor_id')
        date = request.query_params.get('date')
        if not doctor_id or not date:
            return Response({"error": "doctor_id and date are required."}, status=400)
        booked = Appointment.objects.filter(
            doctor_id=doctor_id,
            appointment_date=date,
            status__in=['Pending', 'Confirmed']
        ).values_list('appointment_time', flat=True)
        return Response({"booked_slots": list(booked)})


# ──────────────────────────────────────────────────────────────
# DOCTOR — manage own appointments
# ──────────────────────────────────────────────────────────────

class DoctorAppointmentsView(generics.ListAPIView):
    """GET /api/doctor/appointments/  — doctor sees own schedule"""
    permission_classes = [IsDoctor]
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        qs = Appointment.objects.filter(doctor__user=self.request.user)
        date = self.request.query_params.get('date')
        appt_status = self.request.query_params.get('status')
        if date:
            qs = qs.filter(appointment_date=date)
        if appt_status:
            qs = qs.filter(status=appt_status)
        return qs


class DoctorUpdateAppointmentView(APIView):
    """PATCH /api/doctor/appointments/<pk>/status/  — doctor updates status"""
    permission_classes = [IsDoctor]

    def patch(self, request, pk):
        try:
            appointment = Appointment.objects.get(pk=pk, doctor__user=request.user)
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = AppointmentStatusSerializer(data=request.data)
        if serializer.is_valid():
            appointment.status = serializer.validated_data['status']
            appointment.save()
            return Response({"message": "Appointment status updated.", "appointment": AppointmentSerializer(appointment).data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────────────────────────
# ADMIN — full CRUD
# ──────────────────────────────────────────────────────────────

class AdminAppointmentListView(generics.ListAPIView):
    """GET /api/admin/appointments/"""
    permission_classes = [IsAdmin]
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        qs = Appointment.objects.all()
        appt_status = self.request.query_params.get('status')
        doctor_id = self.request.query_params.get('doctor_id')
        if appt_status:
            qs = qs.filter(status=appt_status)
        if doctor_id:
            qs = qs.filter(doctor_id=doctor_id)
        return qs


class AdminAppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET / PUT / DELETE /api/admin/appointments/<pk>/"""
    permission_classes = [IsAdmin]
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response({"message": "Appointment deleted."}, status=status.HTTP_204_NO_CONTENT)
