<script setup>
import { ref, onMounted } from 'vue';


const patients = ref([]);
const doctors = ref([]);
const departments = ref([]);
const appointments = ref([]);
const loading = ref(true);
const error = ref(null);
const debugInfo = ref('');

function navigateToAddDepartment() {
    window.location.href = '/add-department';
}

function navigateToAddDoctor() {
    window.location.href = '/add-doctor';
}

function navigateToAllDoctors() {
    window.location.href = '/admin/all-doctors';
}

function navigateToAllPatients() {
    window.location.href = '/admin/all-patients';
}

function navigateToAllDepartments() {
    window.location.href = '/admin/all-departments';
}

onMounted(() => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
        error.value = "No authentication token found. Please login first.";
        loading.value = false;
        return;
    }
    debugInfo.value = `Token found: ${token.substring(0, 20)}...`;
    fetch('http://localhost:5000/api/admin-dashboard', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authentication-Token': token
        }
    })
        .then(response => {
            debugInfo.value += `\nResponse status: ${response.status}`;
            return response.text().then(text => ({ status: response.status, text }));
        })
        .then(({ status, text }) => {
            debugInfo.value += `\nResponse length: ${text.length}`;
            if (!text) {
                throw new Error('Empty response from server');
            }
            if (status !== 200) {
                error.value = `Server error (${status}): ${text.substring(0, 200)}`;
                loading.value = false;
                return;
            }
            try {
                const data = JSON.parse(text);
                patients.value = data.patients || [];
                doctors.value = Array.isArray(data.doctors) ? data.doctors : [];
                // If departments array is missing or empty, try to extract unique department names from patients
                if (Array.isArray(data.departments) && data.departments.length > 0) {
                    departments.value = data.departments;
                } else if (Array.isArray(data.patients)) {
                    // Fallback: get unique department names from patients
                    const deptSet = new Set();
                    data.patients.forEach(p => {
                        if (p.department_name) deptSet.add(p.department_name);
                        if (Array.isArray(p.departments)) {
                            p.departments.forEach(d => deptSet.add(d));
                        }
                    });
                    departments.value = Array.from(deptSet);
                } else {
                    departments.value = [];
                }
                // If appointments array is missing or empty, sum appointment_count from patients
                if (Array.isArray(data.appointments) && data.appointments.length > 0) {
                    appointments.value = data.appointments;
                } else if (Array.isArray(data.patients)) {
                    // Fallback: sum appointment_count from all patients
                    const total = data.patients.reduce((sum, p) => sum + (p.appointment_count || 0), 0);
                    appointments.value = Array(total).fill({}); // Just for count
                } else {
                    appointments.value = [];
                }
                loading.value = false;
            } catch (e) {
                error.value = `Invalid JSON response: ${text.substring(0, 100)}`;
                debugInfo.value += `\nJSON parse failed: ${e.message}`;
                loading.value = false;
            }
        })
        .catch(err => {
            error.value = err.message || "Error fetching dashboard data";
            loading.value = false;
        });
});
</script>

<template>
    <div class="admin-dashboard">
        <h2>Admin Dashboard - Patient List</h2>
        
        <div v-if="loading" class="loading">
            <p>Loading patients...</p>
        </div>
        
        <div class="stats-container">
            <div class="stat-item clickable" @click="navigateToAllPatients">
                <span>Total patients: <strong>{{ patients.length }}</strong></span>
            </div>
            <div class="stat-item clickable" @click="navigateToAllDoctors">
                <span>Total doctors: <strong>{{ doctors.length }}</strong></span>
            </div>
            <div class="stat-item clickable" @click="navigateToAllDepartments">
                <span>Total departments: <strong>{{ departments.length }}</strong></span>
            </div>
            <div class="stat-item">
                <span>Total appointments: {{ appointments.length }}</span>
            </div>
        </div>
        
        <div v-if="!loading && !error" class="patients-container">
            <div v-if="patients.length === 0" class="no-patients">
                <p>No patients registered yet.</p>
            </div>
        </div>
        <div>
            <button @click="navigateToAddDepartment">Add Department</button>
            <button @click="navigateToAddDoctor">Add Doctor</button>
        </div>
    </div>
</template>

<style scoped>
.admin-dashboard {
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
}

h2 {
    color: #333;
    margin-bottom: 20px;
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

.debug-info {
    margin-top: 15px;
    text-align: left;
    background-color: #fff3cd;
    border: 1px solid #ffc107;
    border-radius: 4px;
    padding: 10px;
}

.debug-info pre {
    margin: 10px 0 0 0;
    background-color: #f8f9fa;
    padding: 10px;
    border-radius: 3px;
    overflow-x: auto;
    font-size: 12px;
}

.no-patients {
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

.patients-table {
    width: 100%;
    border-collapse: collapse;
    background-color: white;
}

.patients-table thead {
    background-color: #1976d2;
    color: white;
}

.patients-table th {
    padding: 15px;
    text-align: left;
    font-weight: 600;
}

.patients-table td {
    padding: 12px 15px;
    border-bottom: 1px solid #e0e0e0;
}

.patients-table tbody tr:hover {
    background-color: #f5f5f5;
}

.patients-table tbody tr:last-child td {
    border-bottom: none;
}

.stats-container {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
    margin-bottom: 20px;
}

.stat-item {
    padding: 15px;
    background-color: #f5f5f5;
    border-radius: 4px;
    border-left: 4px solid #1976d2;
}

.stat-item.clickable {
    cursor: pointer;
    background-color: #e3f2fd;
    transition: all 0.3s ease;
}

.stat-item.clickable:hover {
    background-color: #bbdefb;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.stat-item strong {
    color: #1976d2;
}
</style>