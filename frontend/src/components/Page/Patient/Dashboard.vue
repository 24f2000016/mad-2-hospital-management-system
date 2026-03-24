<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const currentUserEmail = ref('Loading...');

const logout = () => {
  localStorage.removeItem('auth_token');
  router.push('/');
};

const profile = () => {
  router.push('/dashboard/profile');
};

const schedule_appointment = () => {
  router.push('/dashboard/schedule/doctor');
};

onMounted(async () => {
  const token = localStorage.getItem('auth_token');
  
  if (!token) {
    currentUserEmail.value = 'No user logged in';
    return;
  }

  try {
    const response = await fetch('http://127.0.0.1:5000/api/current-user-details', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authentication-Token': token
      }
    });

    if (response.ok) {
      const data = await response.json();
      
      // Check user role and redirect if not a patient
      const userRoles = data.current_user_roles || [];
      
      if (userRoles.includes('admin')) {
        router.push('/admin-dashboard');
        return;
      } else if (userRoles.includes('doctor')) {
        router.push('/doctor-dashboard');
        return;
      }
      
      // If patient or no role, display user email
      currentUserEmail.value = data.current_user_email || 'Unknown User';
    } else {
      currentUserEmail.value = 'Unable to fetch user data';
    }
  } catch (error) {
    console.error('Error fetching user data:', error);
    currentUserEmail.value = 'Error loading user data';
  }
});
</script>

<template>
    <div>
        <h1>Dashboard</h1>
        <p>Welcome to your personalized dashboard!</p>
        <p><strong>Logged in as:</strong> {{ currentUserEmail }}</p>
        <button @click="profile">Profile</button>
        <button @click="schedule_appointment">Schedule Appointment </button>
        <button @click="logout" >Logout</button>
    </div>
</template>