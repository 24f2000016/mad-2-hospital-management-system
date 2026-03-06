<script setup>
import { ref, onMounted } from 'vue';

const appointments = ref([]);
const loading = ref(true);
const error = ref(null);

function formatTimestamp(timestamp) {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

onMounted(() => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
        error.value = "No authentication token found. Please login first.";
        loading.value = false;
        return;
    }

    fetch('http://localhost:5000/api/admin-dashboard', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authentication-Token': token
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server error (${response.status})`);
            }
            return response.json();
        })
        .then(data => {
            // Get appointments from the response
            if (Array.isArray(data.appointments) && data.appointments.length > 0) {
                appointments.value = data.appointments;
            } else {
                appointments.value = [];
            }
            loading.value = false;
        })
        .catch(err => {
            error.value = err.message || "Error fetching appointments";
            loading.value = false;
        });
});

function goBack() {
    window.location.href = '/admin-dashboard';
}
</script>

<template>
    <div class="all-appointments">
        <div class="header">
            <h2>All Appointments</h2>
            <button @click="goBack" class="back-btn">Back to Dashboard</button>
        </div>

        <div v-if="loading" class="loading">
            <p>Loading appointments...</p>
        </div>

        <div v-else-if="error" class="error">
            <p>{{ error }}</p>
        </div>

        <div v-else>
            <div v-if="appointments.length === 0" class="no-appointments">
                <p>No appointments found.</p>
            </div>
            <div v-else class="table-wrapper">
                <table class="appointments-table">
                    <thead>
                        <tr>
                            <th>Appointment ID</th>
                            <th>Patient</th>
                            <th>Doctor</th>
                            <th>Department</th>
                            <th>Start Time</th>
                            <th>End Time</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="appointment in appointments" :key="appointment.id">
                            <td>{{ appointment.id }}</td>
                            <td>{{ appointment.patient_name }}</td>
                            <td>{{ appointment.doctor_name }}</td>
                            <td>{{ appointment.department_name }}</td>
                            <td>{{ formatTimestamp(appointment.appointment_start_timestamp) }}</td>
                            <td>{{ formatTimestamp(appointment.appointment_end_timestamp) }}</td>
                            <td>{{ appointment.status }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>

<style scoped>
.all-appointments {
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

h2 {
    color: #333;
    margin: 0;
}

.back-btn {
    padding: 10px 20px;
    background-color: #1976d2;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

.back-btn:hover {
    background-color: #1565c0;
}

.loading, .error {
    text-align: center;
    padding: 20px;
    font-size: 16px;
}

.error {
    color: #d32f2f;
    background-color: #ffebee;
    border: 1px solid #d32f2f;
    border-radius: 4px;
}

.no-appointments {
    text-align: center;
    padding: 40px;
    color: #666;
    font-size: 16px;
}

.table-wrapper {
    overflow-x: auto;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.appointments-table {
    width: 100%;
    border-collapse: collapse;
    background-color: white;
}

.appointments-table thead {
    background-color: #1976d2;
    color: white;
}

.appointments-table th {
    padding: 15px;
    text-align: left;
    font-weight: 600;
}

.appointments-table td {
    padding: 12px 15px;
    border-bottom: 1px solid #e0e0e0;
}

.appointments-table tbody tr:hover {
    background-color: #f5f5f5;
}

.appointments-table tbody tr:last-child td {
    border-bottom: none;
}
</style>
