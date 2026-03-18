<script setup>
import { ref, onMounted } from 'vue';

const patients = ref([]);
const loading = ref(true);
const error = ref(null);
const filterName = ref("");
const filterEmail = ref("");
const filterContact = ref("");
const showEditModal = ref(false);
const editingPatient = ref(null);
const editFormData = ref({});
const editLoading = ref(false);
const editError = ref(null);

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

async function blacklistPatient(patient) {
    if (!confirm(`Are you sure you want to blacklist ${patient.full_name}?`)) {
        return;
    }
    
    const token = localStorage.getItem('auth_token');
    try {
        const response = await fetch(`http://localhost:5000/api/patient/${patient.id}/blacklist`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authentication-Token': token
            }
        });
        
        if (response.ok) {
            alert('Patient has been blacklisted');
            fetchPatients();
        } else {
            const data = await response.json();
            alert(`Error: ${data.message}`);
        }
    } catch (err) {
        alert(`Error blacklisting patient: ${err.message}`);
    }
}

async function whitelistPatient(patient) {
    if (!confirm(`Are you sure you want to restore ${patient.full_name} to active status?`)) {
        return;
    }
    
    const token = localStorage.getItem('auth_token');
    try {
        const response = await fetch(`http://localhost:5000/api/patient/${patient.id}/whitelist`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authentication-Token': token
            }
        });
        
        if (response.ok) {
            alert('Patient has been restored to active status');
            fetchPatients();
        } else {
            const data = await response.json();
            alert(`Error: ${data.message}`);
        }
    } catch (err) {
        alert(`Error restoring patient: ${err.message}`);
    }
}

function fetchPatients() {
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
}

function openEditModal(patient) {
    editingPatient.value = patient;
    editFormData.value = {
        id: patient.id,
        full_name: patient.full_name || '',
        user_email: patient.user_email || '',
        dob: patient.dob || '',
        sex: patient.sex || '',
        contact_number: patient.contact_number || ''
    };
    editError.value = null;
    showEditModal.value = true;
}

function closeEditModal() {
    showEditModal.value = false;
    editingPatient.value = null;
    editFormData.value = {};
    editError.value = null;
}

function savePatientDetails() {
    editLoading.value = true;
    editError.value = null;
    
    const token = localStorage.getItem('auth_token');
    if (!token) {
        editError.value = "No authentication token found.";
        editLoading.value = false;
        return;
    }

    fetch(`http://localhost:5000/api/patients/${editFormData.value.id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authentication-Token': token
        },
        body: JSON.stringify(editFormData.value)
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const index = patients.value.findIndex(p => p.id === editFormData.value.id);
            if (index !== -1) {
                patients.value[index] = { ...patients.value[index], ...editFormData.value };
            }
            closeEditModal();
            editLoading.value = false;
        })
        .catch(err => {
            editError.value = err.message || "Error updating patient details";
            editLoading.value = false;
        });
}

onMounted(() => {
    fetchPatients();
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
                        <th>Status</th>
                        <th>Actions</th>
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
                        <td>
                            <span :class="['status-badge', patient.active ? 'active' : 'inactive']">
                                {{ patient.active ? 'Active' : 'Blacklisted' }}
                            </span>
                        </td>
                        <td>
                            <div class="actions-group">
                                <button @click="openEditModal(patient)" class="edit-btn">Edit</button>
                                <button 
                                    v-if="patient.active"
                                    @click="blacklistPatient(patient)" 
                                    class="blacklist-btn"
                                    title="Blacklist this patient"
                                >
                                    Blacklist
                                </button>
                                <button 
                                    v-else
                                    @click="whitelistPatient(patient)" 
                                    class="whitelist-btn"
                                    title="Restore this patient"
                                >
                                    Restore
                                </button>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
            <div class="modal" @click.stop>
                <div class="modal-header">
                    <h3>Edit Patient Details</h3>
                    <button @click="closeEditModal" class="close-btn">×</button>
                </div>
                <div class="modal-body">
                    <div v-if="editError" class="edit-error">{{ editError }}</div>
                    <form @submit.prevent="savePatientDetails">
                        <div class="form-group">
                            <label>Full Name</label>
                            <input v-model="editFormData.full_name" type="text" required />
                        </div>
                        <div class="form-group">
                            <label>Email</label>
                            <input v-model="editFormData.user_email" type="email" required />
                        </div>
                        <div class="form-group">
                            <label>Date of Birth</label>
                            <input v-model="editFormData.dob" type="date" />
                        </div>
                        <div class="form-group">
                            <label>Sex</label>
                            <select v-model="editFormData.sex">
                                <option value="">Select</option>
                                <option value="male">male</option>
                                <option value="female">female</option>
                                <option value="other">other</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Contact Number</label>
                            <input v-model="editFormData.contact_number" type="text" />
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

.edit-btn {
    padding: 6px 12px;
    background-color: #1976d2;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
    transition: background-color 0.3s ease;
}

.edit-btn:hover {
    background-color: #1565c0;
}

.blacklist-btn {
    padding: 6px 12px;
    background-color: #d32f2f;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
    transition: background-color 0.3s ease;
}

.blacklist-btn:hover {
    background-color: #b71c1c;
}

.whitelist-btn {
    padding: 6px 12px;
    background-color: #388e3c;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
    transition: background-color 0.3s ease;
}

.whitelist-btn:hover {
    background-color: #2e7d32;
}

.actions-group {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.status-badge {
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
    white-space: nowrap;
}

.status-badge.active {
    background-color: #e8f5e9;
    color: #2e7d32;
}

.status-badge.inactive {
    background-color: #ffebee;
    color: #c62828;
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
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    max-width: 500px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    border-bottom: 1px solid #e0e0e0;
    background-color: #f5f5f5;
}

.modal-header h3 {
    margin: 0;
    color: #333;
}

.close-btn {
    background: none;
    border: none;
    font-size: 28px;
    cursor: pointer;
    color: #666;
    padding: 0;
    width: 32px;
    height: 32px;
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
    background-color: #ffebee;
    color: #d32f2f;
    padding: 12px;
    border-radius: 4px;
    margin-bottom: 15px;
    border: 1px solid #d32f2f;
}

.form-group {
    margin-bottom: 15px;
    display: flex;
    flex-direction: column;
}

.form-group label {
    font-weight: 600;
    margin-bottom: 5px;
    color: #333;
    font-size: 14px;
}

.form-group input,
.form-group select {
    padding: 8px 12px;
    border: 1px solid #bdbdbd;
    border-radius: 4px;
    font-size: 14px;
    font-family: inherit;
    transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus {
    outline: none;
    border-color: #1976d2;
    box-shadow: 0 0 4px rgba(25, 118, 210, 0.2);
}

.form-actions {
    display: flex;
    gap: 10px;
    margin-top: 20px;
    justify-content: flex-end;
}

.save-btn {
    padding: 10px 20px;
    background-color: #4caf50;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    transition: background-color 0.3s ease;
}

.save-btn:hover:not(:disabled) {
    background-color: #45a049;
}

.save-btn:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
}

.cancel-btn {
    padding: 10px 20px;
    background-color: #9e9e9e;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    transition: background-color 0.3s ease;
}

.cancel-btn:hover:not(:disabled) {
    background-color: #757575;
}

.cancel-btn:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
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