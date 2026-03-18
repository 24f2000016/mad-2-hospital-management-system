<script setup>
import { onMounted, ref, computed } from 'vue';
const doctors = ref([]);
const departments = ref([]);
const selectedDoctorId = ref(sessionStorage.getItem('selectedDoctorId'));
const searchName = ref('');
const searchDepartment = ref('');

const selectedDoctor = computed(() => {
    return doctors.value.find(doc => doc.id === parseInt(selectedDoctorId.value));
});

const filteredDoctors = computed(() => {
    return doctors.value.filter(doctor => {
        const nameMatch = doctor.full_name.toLowerCase().includes(searchName.value.toLowerCase());
        const departmentMatch = searchDepartment.value === '' || doctor.department === searchDepartment.value;
        
        return nameMatch && departmentMatch;
    });
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

async function fetchDepartments() {
    const token = localStorage.getItem('auth_token');
    try {
        const response = await fetch('http://127.0.0.1:5000/api/departments', {
            method: 'GET',
            headers: {
                'Authentication-Token': token
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            departments.value = data.departments || [];
            console.log('Departments fetched:', departments.value);
        } else {
            const errorText = await response.text();
            console.error('Failed to fetch departments. Status:', response.status, 'Response:', errorText);
        }
    } catch (err) {
        console.error('Failed to fetch departments:', err);
    }
}

function selectDoctor(doctorId) {
    selectedDoctorId.value = doctorId;
    sessionStorage.setItem('selectedDoctorId', doctorId);
    console.log('Selected doctor ID:', doctorId);
}

onMounted(() => {
    fetchDoctors();
    fetchDepartments();
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
    
    <!-- Filter Section -->
    <div class="filters-section">
        <div class="filter-group">
            <label>Search by Name:</label>
            <input 
                v-model="searchName" 
                type="text" 
                placeholder="Enter doctor name..."
                class="filter-input"
            />
        </div>
        <div class="filter-group">
            <label>Filter by Specialization:</label>
            <select v-model="searchDepartment" class="filter-input">
                <option value="">All Specializations</option>
                <option v-for="dept in departments" :key="dept.id" :value="dept.name">
                    {{ dept.name }}
                </option>
            </select>
        </div>
    </div>
    
    <div v-if="doctors.length === 0">
        No doctors available.
    </div>
    <div v-else-if="filteredDoctors.length === 0" class="no-results">
        No doctors match your search criteria.
    </div>
    <ul v-else class="doctors-list">
        <li v-for="doctor in filteredDoctors" :key="doctor.id" @click="selectDoctor(doctor.id)" class="doctor-item">
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

<style scoped>
.filters-section {
    display: flex;
    gap: 15px;
    margin-bottom: 25px;
    flex-wrap: wrap;
    background-color: #f9f9f9;
    padding: 15px;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
}

.filter-group {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-width: 200px;
}

.filter-group label {
    margin-bottom: 5px;
    color: #333;
    font-weight: 500;
    font-size: 14px;
}

.filter-input {
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    background-color: white;
}

.filter-input:focus {
    outline: none;
    border-color: #1976d2;
    box-shadow: 0 0 3px rgba(25, 118, 210, 0.5);
}

.no-results {
    padding: 20px;
    text-align: center;
    color: #666;
    font-size: 16px;
}

.doctors-list {
    list-style: none;
    padding: 0;
    margin: 0 0 20px 0;
}

.doctor-item {
    padding: 12px 15px;
    margin-bottom: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.doctor-item:hover {
    background-color: #f5f5f5;
    border-color: #1976d2;
    box-shadow: 0 2px 4px rgba(25, 118, 210, 0.2);
}
</style>