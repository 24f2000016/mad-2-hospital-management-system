<script setup>
import { ref, onMounted } from 'vue';

const patients = ref([]);
const loading = ref(true);
const error = ref(null);
const filterName = ref("");
const filterEmail = ref("");
const filterContact = ref("");

import { computed } from 'vue';
const filteredPatients = computed(() => {
    const nameFilter = filterName.value.trim().toLowerCase();
    const emailFilter = filterEmail.value.trim().toLowerCase();
    const contactFilter = filterContact.value.trim().toLowerCase();
    
    return patients.value.filter(p => {
        const matchName = !nameFilter || (p.full_name && p.full_name.toLowerCase().includes(nameFilter));
        const matchEmail = !emailFilter || (p.user_email && p.user_email.toLowerCase().includes(emailFilter));
        const matchContact = !contactFilter || (p.contact_number && String(p.contact_number).toLowerCase().includes(contactFilter));
        
        return matchName && matchEmail && matchContact;
    });
});

function goBack() {
    window.location.href = '/admin-dashboard';
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
                throw new Error(`Server error: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            patients.value = data.patients || [];
            loading.value = false;
        })
        .catch(err => {
            error.value = err.message || "Error fetching patients data";
            loading.value = false;
        });
});
</script>

<template>
    <div class="all-patients">
        <div class="header">
            <h2>All Patients</h2>
            <button @click="goBack" class="back-btn">← Back to Dashboard</button>
        </div>

        <div class="filter-bar">
            <input
                v-model="filterName"
                type="text"
                placeholder="Filter by name"
                class="filter-input"
            />
            <input
                v-model="filterEmail"
                type="text"
                placeholder="Filter by email"
                class="filter-input"
            />
            <input
                v-model="filterContact"
                type="text"
                placeholder="Filter by contact number"
                class="filter-input"
            />
        </div>

        <div v-if="loading" class="loading">
            <p>Loading patients...</p>
        </div>

        <div v-else-if="error" class="error">
            <p>{{ error }}</p>
        </div>

        <div v-else-if="filteredPatients.length === 0" class="no-patients">
            <p>No patients found for the given filters.</p>
        </div>

        <div v-else class="table-wrapper">
            <table class="patients-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Full Name</th>
                        <th>Email</th>
                        <th>Date of Birth</th>
                        <th>Age</th>
                        <th>Sex</th>
                        <th>Contact Number</th>
                        <th>Appointments</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="patient in filteredPatients" :key="patient.id">
                        <td>{{ patient.id }}</td>
                        <td>{{ patient.full_name || 'N/A' }}</td>
                        <td>{{ patient.user_email || 'N/A' }}</td>
                        <td>{{ patient.dob || 'N/A' }}</td>
                        <td>{{ patient.age || 'N/A' }}</td>
                        <td>{{ patient.sex || 'N/A' }}</td>
                        <td>{{ patient.contact_number || 'N/A' }}</td>
                        <td>{{ patient.appointment_count }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<style scoped>
.all-patients {
    padding: 20px;
    max-width: 1400px;
    margin: 0 auto;
}

.filter-bar {
    margin-bottom: 20px;
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.filter-input {
    padding: 8px 14px;
    border: 1px solid #bdbdbd;
    border-radius: 4px;
    font-size: 15px;
    flex: 1;
    min-width: 200px;
    outline: none;
    transition: border-color 0.2s;
}
.filter-input:focus {
    border-color: #1976d2;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}

h2 {
    color: #333;
    margin: 0;
}

.back-btn {
    padding: 10px 20px;
    background-color: #6c757d;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    transition: background-color 0.3s ease;
}

.back-btn:hover {
    background-color: #5a6268;
}

.loading, .error {
    text-align: center;
    padding: 40px 20px;
    font-size: 16px;
}

.error {
    color: #d32f2f;
    background-color: #ffebee;
    border: 1px solid #d32f2f;
    border-radius: 4px;
}

.no-patients {
    text-align: center;
    padding: 40px;
    color: #666;
    font-size: 16px;
    background-color: #f5f5f5;
    border-radius: 4px;
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
    white-space: nowrap;
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

@media (max-width: 768px) {
    .header {
        flex-direction: column;
        gap: 15px;
        align-items: flex-start;
    }

    .back-btn {
        width: 100%;
    }

    .patients-table th,
    .patients-table td {
        padding: 8px 10px;
        font-size: 14px;
    }
}
</style>