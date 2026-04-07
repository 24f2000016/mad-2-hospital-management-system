<script setup>
import { ref } from 'vue';
const username = ref('');
const first_name = ref('');
const last_name = ref('');
const dob = ref('');
const sex = ref('');
const contact_number = ref('');
const email = ref('');
const password = ref('');

async function update() {
  const token = localStorage.getItem('auth_token');
  try {
    const response = await fetch('http://127.0.0.1:5000/api/profile', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authentication-Token': token
      },
      body: JSON.stringify({ 
        username: username.value, 
        first_name: first_name.value, 
        last_name: last_name.value, 
        dob: dob.value, 
        sex: sex.value,
        contact_number: contact_number.value,
        email: email.value,
        password: password.value
      })
    });
    if (response.ok) {
      alert('Profile updated successfully');
    } else {
      alert('Failed to update profile');
    }
  } catch (error) {
    console.error('Error updating profile:', error);
  }
}

</script>

<template>
  <div class="profile-section">
    <div class="profile-group">
      <label for="username">Username: </label>
      <input v-model="username" id="username" type="text" placeholder="username">
    </div>
    <div class="profile-group">
      <label for="first_name">First name: </label>
      <input v-model="first_name" id="first_name" type="text" placeholder="first name">
    </div>
    <div class="profile-group">
      <label for="last_name">Last name: </label>
      <input v-model="last_name" id="last_name" type="text" placeholder="last name">
    </div>
    <div class="profile-group">
      <label for="dob">Date of birth: </label>
      <input v-model="dob" id="dob" type="date" placeholder="date of birth">
    </div>
    <div class="profile-group">
      <label for="contact_number">Contact number: </label>
      <input v-model="contact_number" id="contact_number" type="text" placeholder="contact number">
    </div>
    <div class="profile-group">
      <label for="email">Email: </label>
      <input v-model="email" id="email" type="email" placeholder="email">
    </div>
    <div class="profile-group">
      <label for="password">Password: </label>
      <input v-model="password" id="password" type="password" placeholder="password">
    </div>
    <div class="profile-group">
      <label for="sex">Sex: </label>
      <select v-model="sex" id="sex">
        <option disabled value="">Sex</option>
        <option value="male">Male</option>
        <option value="female">Female</option>
        <option value="other">Other</option>
      </select>
    </div>
    <button @click="update" class="blue-btn">Update</button>
  </div>
</template>

<style scoped>
.profile-section{
  display: flex;
  gap: 15px;
  margin-bottom: 25px;
  flex-wrap: wrap;
  background-color: #f8f8f8;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #c3c3c3;
}  

.profile-group{
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 200px;
}

.profile-group label{
  margin-bottom: 5px;
  color: #333;
  font-weight: 500;
  font-size: 14px;
}

.blue-btn {
  padding: 6px 12px;
  background-color: #1976d2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: background-color 0.3s ease;
}

.blue-btn:hover {
  background-color: #0655af;
}
</style>