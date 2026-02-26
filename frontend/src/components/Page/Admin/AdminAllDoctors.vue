<script setup>
import { ref, onMounted } from 'vue';

const doctors = ref([]);
const departments = ref([]);
const loading = ref(true);
const error = ref(null);
const editingDoctor = ref(null);
const showEditForm = ref(false);

const editForm = ref({
    full_name: '',
    email: '',
    experience: '',
    department_id: '',
    username: ''
});

onMounted(() => {
    fetchDoctors();
    fetchDepartments();
});

async function fetchDoctors() {
    const token = localStorage.getItem('auth_token');
    try {
        const response = await fetch('http://localhost:5000/api/doctor', {
            method: 'GET',
            headers: {
                'Authentication-Token': token
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            doctors.value = data.doctors || [];
        } else {
            error.value = 'Failed to fetch doctors';
        }
    } catch (err) {
        error.value = err.message;
    } finally {
        loading.value = false;
    }
}

async function fetchDepartments() {
    const token = localStorage.getItem('auth_token');
    try {
        const response = await fetch('http://localhost:5000/api/departments', {
            method: 'GET',
            headers: {
                'Authentication-Token': token
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            departments.value = data.departments || [];
        }
    } catch (err) {
        console.error('Failed to fetch departments:', err);
    }
}

function openEditForm(doctor) {
    editingDoctor.value = doctor;
    editForm.value = {
        full_name: doctor.full_name,
        email: doctor.email,
        experience: doctor.experience,
        department_id: doctor.department,
        username: doctor.username || ''
    };
    showEditForm.value = true;
}

function closeEditForm() {
    showEditForm.value = false;
    editingDoctor.value = null;
}

async function saveDoctor() {
    if (!editingDoctor.value) return;
    
    const token = localStorage.getItem('auth_token');
    try {
        const response = await fetch(`http://localhost:5000/api/doctor/${editingDoctor.value.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authentication-Token': token
            },
            body: JSON.stringify({
                full_name: editForm.value.full_name,
                email: editForm.value.email,
                experience: editForm.value.experience,
                department_id: editForm.value.department_id,
                username: editForm.value.username
            })
        });
        
        if (response.ok) {
            alert('Doctor updated successfully');
            closeEditForm();
            fetchDoctors();
        } else {
            const data = await response.json();
            alert(`Error: ${data.message}`);
        }
    } catch (err) {
        alert(`Error updating doctor: ${err.message}`);
    }
}

function goBack() {
    window.location.href = '/admin-dashboard';
}
</script>

<template>
    <div class="admin-all-doctors">
        <div class="header">
            <h2>All Doctors</h2>
            <button @click="goBack" class="back-btn">Back to Dashboard</button>
        </div>
        
        <div v-if="loading" class="loading">
            <p>Loading doctors...</p>
        </div>
        
        <div v-if="error" class="error">
            {{ error }}
        </div>
        
        <div v-if="!loading && !error" class="doctors-container">
            <div v-if="doctors.length === 0" class="no-doctors">
                <p>No doctors found.</p>
            </div>
            
            <div v-else class="table-wrapper">
                <table class="doctors-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Full Name</th>
                            <th>Email</th>
                            <th>Department</th>
                            <th>Experience</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="doctor in doctors" :key="doctor.id">
                            <td>{{ doctor.id }}</td>
                            <td>{{ doctor.full_name }}</td>
                            <td>{{ doctor.email }}</td>
                            <td>{{ doctor.department }}</td>
                            <td>{{ doctor.experience }}</td>
                            <td>
                                <button @click="openEditForm(doctor)" class="edit-btn">Edit</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Edit Form Modal -->
        <div v-if="showEditForm" class="modal-overlay" @click="closeEditForm">
            <div class="modal-content" @click.stop>
                <h3>Edit Doctor</h3>
                <form @submit.prevent="saveDoctor">
                    <div class="form-group">
                        <label>Full Name:</label>
                        <input v-model="editForm.full_name" type="text" required />
                    </div>
                    <div class="form-group">
                        <label>Email:</label>
                        <input v-model="editForm.email" type="email" required />
                    </div>
                    <div class="form-group">
                        <label>Username:</label>
                        <input v-model="editForm.username" type="text" />
                    </div>
                    <div class="form-group">
                        <label>Experience:</label>
                        <input v-model="editForm.experience" type="text" />
                    </div>
                    <div class="form-group">
                        <label>Department:</label>
                        <select v-model="editForm.department_id" required>
                            <option disabled value="">Select Department</option>
                            <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                                {{ dept.name }}
                            </option>
                        </select>
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="save-btn">Save</button>
                        <button type="button" @click="closeEditForm" class="cancel-btn">Cancel</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<style scoped>
.admin-all-doctors {
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

.header h2 {
    color: #333;
    margin: 0;
}

.back-btn {
    padding: 8px 16px;
    background-color: #757575;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

.back-btn:hover {
    background-color: #616161;
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

.no-doctors {
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

.doctors-table {
    width: 100%;
    border-collapse: collapse;
    background-color: white;
}

.doctors-table thead {
    background-color: #1976d2;
    color: white;
}

.doctors-table th {
    padding: 15px;
    text-align: left;
    font-weight: 600;
}

.doctors-table td {
    padding: 12px 15px;
    border-bottom: 1px solid #e0e0e0;
}

.doctors-table tbody tr:hover {
    background-color: #f5f5f5;
}

.doctors-table tbody tr:last-child td {
    border-bottom: none;
}

.edit-btn {
    padding: 6px 12px;
    background-color: #1976d2;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

.edit-btn:hover {
    background-color: #1565c0;
}

/* Modal Styles */
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

.modal-content {
    background-color: white;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    max-width: 500px;
    width: 90%;
}

.modal-content h3 {
    margin-top: 0;
    color: #333;
}

.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    color: #333;
    font-weight: 500;
}

.form-group input,
.form-group select {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus {
    outline: none;
    border-color: #1976d2;
    box-shadow: 0 0 3px rgba(25, 118, 210, 0.5);
}

.form-actions {
    display: flex;
    gap: 10px;
    justify-content: flex-end;
    margin-top: 20px;
}

.save-btn {
    padding: 10px 20px;
    background-color: #4caf50;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

.save-btn:hover {
    background-color: #45a049;
}

.cancel-btn {
    padding: 10px 20px;
    background-color: #757575;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

.cancel-btn:hover {
    background-color: #616161;
}
</style>