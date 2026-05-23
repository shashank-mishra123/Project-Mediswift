from rest_framework import serializers
from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    doctor_specialty = serializers.CharField(source='doctor.specialty', read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['id', 'booking_ref', 'created_at', 'updated_at']


class AppointmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['doctor', 'patient_name', 'patient_mobile', 'appointment_date', 'appointment_time', 'notes']

    def validate(self, data):
        # Check slot availability
        exists = Appointment.objects.filter(
            doctor=data['doctor'],
            appointment_date=data['appointment_date'],
            appointment_time=data['appointment_time'],
            status__in=['Pending', 'Confirmed']
        ).exists()
        if exists:
            raise serializers.ValidationError("This slot is already booked.")
        return data


class AppointmentStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['Pending', 'Confirmed', 'Completed', 'Cancelled'])
