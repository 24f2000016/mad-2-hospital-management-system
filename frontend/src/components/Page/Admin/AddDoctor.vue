<script setup>
import { onMounted, ref } from 'vue';
const doctor_full_name = ref('');
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
                doctor_full_name: doctor_full_name.value, 
                doctor_department_id: doctor_department_id.value,
                doctor_experience: doctor_experience.value
            })
        });

        if (response.ok) {
            alert("Doctor added successfully!");
        } else {
            alert("Failed to add doctor.");
        }
    } catch (error) {
        console.error("Error adding doctor:", error);
        alert("Error adding doctor.");
    }
}

</script>

<template>
    <h2>Add Doctor</h2>
    <div>
        <input v-model="doctor_full_name" type="text" placeholder="Enter doctor's full name" >
        <input v-model="doctor_password" type="password" placeholder="set password for doctor" >
        <input v-model="doctor_email" type="text" placeholder="Enter doctor's email">
        <input v-model="doctor_experience" type="text" placeholder="Enter doctor's experience">
        <input v-model="doctor_username" type="text" placeholder="Set doctor's username">
        <select v-model="doctor_department_id">
            <option disabled value="">Select Department</option>
            <option v-for="department in departments" :key="department.id" :value="department.id">
                {{ department.name }}
            </option>
        </select>
        <button @click="addDoctor">Add Doctor</button>
    </div>
</template>