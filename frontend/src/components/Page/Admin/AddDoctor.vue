<script setup>
import { onMounted, ref } from 'vue';
const doctor_first_name = ref('');
const doctor_last_name = ref('');
const doctor_password = ref('');
const doctor_email = ref('');
const doctor_experience = ref('');
const doctor_username = ref('');
const doctor_department_id = ref('');
const departments = ref([]);
const token = localStorage.getItem('auth_token');




onMounted(() => {
    fetchDepartments();
});



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
            departments.value = data.departments;
            console.log('Departments:', data.departments);
        } else {
            const errorText = await response.text();
            console.error('Failed to fetch departments:', errorText);
        }
    } catch (error) {
        console.error('Error fetching departments:', error);
    }
}







async function addDoctor() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/doctor', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authentication-Token': token
            },
            body: JSON.stringify({ 
                doctor_email: doctor_email.value,
                doctor_username: doctor_username.value,
                doctor_password: doctor_password.value,
                doctor_first_name: doctor_first_name.value,
                doctor_last_name: doctor_last_name.value,
                doctor_department_id: doctor_department_id.value,
                doctor_experience: doctor_experience.value
            })
        });

        if (response.ok) {
            alert("Doctor added successfully!");
            // Clear form
            doctor_first_name.value = '';
            doctor_last_name.value = '';
            doctor_password.value = '';
            doctor_email.value = '';
            doctor_experience.value = '';
            doctor_username.value = '';
            doctor_department_id.value = '';
        } else {
            const errorData = await response.json();
            alert("Failed to add doctor: " + (errorData.message || "Unknown error"));
        }
    } catch (error) {
        console.error("Error adding doctor:", error);
        alert("Error adding doctor.");
    }
}

</script>

<style scoped>
.add-doctor-container {
    padding: 20px;
    max-width: 600px;
    margin: 0 auto;
}

h2 {
    color: #333;
    margin-bottom: 20px;
    text-align: center;
}

.form-container {
    display: flex;
    flex-direction: column;
    gap: 15px;
    background-color: #f5f5f5;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

input,
select {
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    font-family: inherit;
}

input:focus,
select:focus {
    outline: none;
    border-color: #1976d2;
    box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.add-btn {
    padding: 12px;
    background-color: #1976d2;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.3s ease;
    margin-top: 10px;
}

.add-btn:hover {
    background-color: #1565c0;
}

.add-btn:active {
    background-color: #0d47a1;
}
</style>

<template>
    <div class="add-doctor-container">
        <h2>Add Doctor</h2>
        <div class="form-container">
            <input v-model="doctor_first_name" type="text" placeholder="Enter doctor's first name">
            <input v-model="doctor_last_name" type="text" placeholder="Enter doctor's last name">
            <input v-model="doctor_email" type="email" placeholder="Enter doctor's email">
            <input v-model="doctor_username" type="text" placeholder="Set doctor's username">
            <input v-model="doctor_password" type="password" placeholder="Set password for doctor">
            <input v-model="doctor_experience" type="text" placeholder="Enter doctor's experience">
            <select v-model="doctor_department_id">
                <option disabled value="">Select Department</option>
                <option v-for="department in departments" :key="department.id" :value="department.id">
                    {{ department.name }}
                </option>
            </select>
            <button @click="addDoctor" class="add-btn">Add Doctor</button>
        </div>
    </div>
</template>