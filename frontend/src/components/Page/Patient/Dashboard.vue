<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const currentUserEmail = ref('Loading...');

const logout = () => {
  router.push('/logout');
};

const medical_history = () => {
  router.push('/patient/my-history');
};

const profile = () => {
  router.push('/dashboard/profile');
};

const schedule_appointment = () => {
  router.push('/dashboard/schedule/doctor');
};

const my_appointments = () => {
  router.push('/patient/my-appointments');
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
        <div class="action-buttons">
          <button @click="profile" class="blue-btn">Profile</button>
          <button @click="schedule_appointment" class="blue-btn">Schedule Appointment </button>
          <button @click="my_appointments" class="blue-btn">My Appointments</button>
          <button @click="medical_history" class="blue-btn">My Medical History</button>
          <button @click="logout" class="red-btn">Logout</button>
        </div>
    </div>
</template>

<style scoped>
.dashboard{
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif
}

.action-buttons {
    display: flex;
    gap: 10px;
    margin-top: 20px;
    justify-content: flex;
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

.red-btn {
  padding: 6px 12px;
    background-color: #d21919;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
    transition: background-color 0.3s ease;
}

.red-btn:hover {
    background-color: #af0606;
}
</style>