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
  <div>
    <input v-model="username" type="text" placeholder="username" />
    <input v-model="first_name" type="text" placeholder="first name">
    <input v-model="last_name" type="text" placeholder="last name">
    <input v-model="dob" type="date" placeholder="date of birth">
    <input v-model="contact_number" type="text" placeholder="contact number">
    <input v-model="email" type="email" placeholder="email" />
    <input v-model="password" type="password" placeholder="password" />
    <select v-model="sex">
      <option disabled value="">Sex</option>
      <option value="male">Male</option>
      <option value="female">Female</option>
      <option value="other">Other</option>
    </select>
    <button @click="update">Update</button>
  </div>
</template>

<style scoped>  
</style>