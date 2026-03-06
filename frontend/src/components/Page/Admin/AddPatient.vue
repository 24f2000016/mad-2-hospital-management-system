<script setup>
import { ref } from 'vue';

const patient_first_name = ref('');
const patient_last_name = ref('');
const patient_password = ref('');
const patient_email = ref('');
const patient_dob = ref('');
const patient_sex = ref('');
const patient_contact_number = ref('');
const patient_username = ref('');
const token = localStorage.getItem('auth_token');

async function addPatient() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/patient', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authentication-Token': token
            },
            body: JSON.stringify({
                patient_email: patient_email.value,
                patient_username: patient_username.value,
                patient_password: patient_password.value,
                patient_first_name: patient_first_name.value,
                patient_last_name: patient_last_name.value,
                patient_dob: patient_dob.value,
                patient_sex: patient_sex.value,
                patient_contact_number: patient_contact_number.value
            })
        });

        if (response.ok) {
            alert("Patient added successfully!");
            // Clear form
            patient_first_name.value = '';
            patient_last_name.value = '';
            patient_password.value = '';
            patient_email.value = '';
            patient_dob.value = '';
            patient_sex.value = '';
            patient_contact_number.value = '';
            patient_username.value = '';
        } else {
            const errorData = await response.json();
            alert("Failed to add patient: " + (errorData.message || "Unknown error"));
        }
    } catch (error) {
        console.error("Error adding patient:", error);
        alert("Error adding patient: " + error.message);
    }
}
</script>

<template>
    <div class="add-patient-container">
        <h2>Add Patient</h2>
        <div class="form-container">
            <input v-model="patient_first_name" type="text" placeholder="Enter patient's first name">
            <input v-model="patient_last_name" type="text" placeholder="Enter patient's last name">
            <input v-model="patient_email" type="email" placeholder="Enter patient's email">
            <input v-model="patient_username" type="text" placeholder="Set patient's username">
            <input v-model="patient_password" type="password" placeholder="Set password for patient">
            <input v-model="patient_dob" type="date" placeholder="Select date of birth">
            <select v-model="patient_sex">
                <option disabled value="">Select Gender</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
            </select>
            <input v-model="patient_contact_number" type="tel" placeholder="Enter contact number">
            <button @click="addPatient" class="add-btn">Add Patient</button>
        </div>
    </div>
</template>

<style scoped>
.add-patient-container {
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
