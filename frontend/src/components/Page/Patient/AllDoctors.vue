<script setup>
import { onMounted, ref, computed } from 'vue';
const doctors = ref([]);
const selectedDoctorId = ref(sessionStorage.getItem('selectedDoctorId'));

const selectedDoctor = computed(() => {
    return doctors.value.find(doc => doc.id === parseInt(selectedDoctorId.value));
});

async function fetchDoctors() {
    const token = localStorage.getItem('auth_token');
    try {
        const response = await fetch('http://127.0.0.1:5000/api/doctor', {
            method: 'GET',
            headers: {
                'Authentication-Token': token   
            }
        });
        if (response.ok) {
            const data = await response.json();
            doctors.value = data.doctors;
            console.log('Doctors:', data.doctors);
        } else {
            const errorText = await response.text();
            console.error('Failed to fetch doctors:', errorText);
        }
    } catch (error) {
        console.error('Error fetching doctors:', error);
    }
}

function selectDoctor(doctorId) {
    selectedDoctorId.value = doctorId;
    sessionStorage.setItem('selectedDoctorId', doctorId);
    console.log('Selected doctor ID:', doctorId);
}

onMounted(() => {
    fetchDoctors();
});

async function scheduleAppointment() {
    if (!selectedDoctor.value) {
        alert('Please select a doctor first.');
        return;
    }

    alert(`Scheduling appointment with Dr. ${selectedDoctor.value.full_name}`);
    window.location.href = `/dashboard/schedule/doctor/appointment`;
}


</script>

<template>
    <h3>Select Doctor</h3>
    <div v-if="doctors.length === 0">
        No doctors available.
    </div>
    <ul v-else>
        <li v-for="doctor in doctors" :key="doctor.id" @click="selectDoctor(doctor.id)" style="cursor: pointer;">
            {{ doctor.full_name }} - {{ doctor.department }}
        </li>
    </ul>

    <div v-if="selectedDoctor" style="margin-top: 20px; padding: 15px; border: 1px solid #ccc; border-radius: 4px;">
        <h4>Selected Doctor</h4>
        <p><strong>Name:</strong> Dr. {{ selectedDoctor.full_name }}</p>
        <p><strong>Department:</strong> {{ selectedDoctor.department }}</p>
        <p><strong>ID:</strong> {{ selectedDoctor.id }}</p>
    </div>

    <button @click="scheduleAppointment">Schedule Appointment</button>
</template>