<script setup>
import { ref, onMounted } from 'vue';

const appointments = ref([]);
const loading = ref(true);
const error = ref(null);
const showEditModal = ref(false);
const editingAppointment = ref(null);
const editFormData = ref({});
const editLoading = ref(false);
const editError = ref(null);

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

function modifyAppointment(appointment) {
    editingAppointment.value = appointment;
    // Convert ISO format to datetime-local format (remove 'Z' and milliseconds)
    const startTime = appointment.appointment_start_timestamp ? appointment.appointment_start_timestamp.split('.')[0] : '';
    const endTime = appointment.appointment_end_timestamp ? appointment.appointment_end_timestamp.split('.')[0] : '';
    
    editFormData.value = {
        id: appointment.id,
        appointment_start_timestamp: startTime,
        appointment_end_timestamp: endTime,
        status: appointment.status
    };
    editError.value = null;
    showEditModal.value = true;
}

function closeEditModal() {
    showEditModal.value = false;
    editingAppointment.value = null;
    editFormData.value = {};
    editError.value = null;
}

function saveAppointmentDetails() {
    editLoading.value = true;
    editError.value = null;
    
    const token = localStorage.getItem('auth_token');
    if (!token) {
        editError.value = "No authentication token found.";
        editLoading.value = false;
        return;
    }

    // Convert datetime-local format back to ISO format
    const payload = {
        id: editFormData.value.id,
        appointment_start_timestamp: editFormData.value.appointment_start_timestamp ? new Date(editFormData.value.appointment_start_timestamp).toISOString() : '',
        appointment_end_timestamp: editFormData.value.appointment_end_timestamp ? new Date(editFormData.value.appointment_end_timestamp).toISOString() : '',
        status: editFormData.value.status
    };

    fetch(`http://localhost:5000/api/appointments/${editFormData.value.id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authentication-Token': token
        },
        body: JSON.stringify(payload)
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const index = appointments.value.findIndex(a => a.id === editFormData.value.id);
            if (index !== -1) {
                // Update with ISO format timestamps
                appointments.value[index] = {
                    ...appointments.value[index],
                    appointment_start_timestamp: payload.appointment_start_timestamp,
                    appointment_end_timestamp: payload.appointment_end_timestamp,
                    status: editFormData.value.status
                };
            }
            closeEditModal();
            editLoading.value = false;
        })
        .catch(err => {
            editError.value = err.message || "Error updating appointment details";
            editLoading.value = false;
        });
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
                            <th>Action</th>
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
                            <td>
                                <button @click="modifyAppointment(appointment)" class="modify-btn">Modify</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
        <div class="modal" @click.stop>
            <div class="modal-header">
                <h3>Edit Appointment</h3>
                <button @click="closeEditModal" class="close-btn">×</button>
            </div>
            <div class="modal-body">
                <div v-if="editError" class="edit-error">{{ editError }}</div>
                <form @submit.prevent="saveAppointmentDetails">
                    <div class="form-group">
                        <label>Start Time</label>
                        <input v-model="editFormData.appointment_start_timestamp" type="datetime-local" required />
                    </div>
                    <div class="form-group">
                        <label>End Time</label>
                        <input v-model="editFormData.appointment_end_timestamp" type="datetime-local" required />
                    </div>
                    <div class="form-group">
                        <label>Status</label>
                        <select v-model="editFormData.status" required>
                            <option value="booked">Booked</option>
                            <option value="completed">Completed</option>
                            <option value="canceled">Canceled</option>
                        </select>
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="save-btn" :disabled="editLoading">
                            {{ editLoading ? 'Saving...' : 'Save' }}
                        </button>
                        <button type="button" class="cancel-btn" @click="closeEditModal" :disabled="editLoading">
                            Cancel
                        </button>
                    </div>
                </form>
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

.modify-btn {
    padding: 6px 12px;
    background-color: #4caf50;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
    font-weight: 500;
}

.modify-btn:hover {
    background-color: #45a049;
}

.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.modal {
    background-color: white;
    border-radius: 8px;
    width: 90%;
    max-width: 500px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    border-bottom: 1px solid #e0e0e0;
}

.modal-header h3 {
    margin: 0;
    color: #333;
}

.close-btn {
    background: none;
    border: none;
    font-size: 28px;
    color: #999;
    cursor: pointer;
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.close-btn:hover {
    color: #333;
}

.modal-body {
    padding: 20px;
}

.edit-error {
    color: #d32f2f;
    background-color: #ffebee;
    border: 1px solid #d32f2f;
    border-radius: 4px;
    padding: 12px;
    margin-bottom: 16px;
}

.form-group {
    margin-bottom: 16px;
}

.form-group label {
    display: block;
    margin-bottom: 6px;
    color: #333;
    font-weight: 500;
}

.form-group input,
.form-group select {
    width: 100%;
    padding: 10px;
    border: 1px solid #bdbdbd;
    border-radius: 4px;
    font-size: 14px;
    box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus {
    outline: none;
    border-color: #1976d2;
    box-shadow: 0 0 0 3px rgba(25, 118, 210, 0.1);
}

.form-actions {
    display: flex;
    gap: 10px;
    margin-top: 24px;
}

.save-btn,
.cancel-btn {
    flex: 1;
    padding: 12px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
}

.save-btn {
    background-color: #4caf50;
    color: white;
}

.save-btn:hover:not(:disabled) {
    background-color: #45a049;
}

.cancel-btn {
    background-color: #f5f5f5;
    color: #333;
}

.cancel-btn:hover:not(:disabled) {
    background-color: #e0e0e0;
}

.save-btn:disabled,
.cancel-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}
</style>
