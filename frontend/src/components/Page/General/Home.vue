<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const token = ref(localStorage.getItem('auth_token'));
const router = useRouter();

const patientLogin = () => {
  router.push("/login")
}

const staffLogin = () => {
  router.push("/staff-login")
}

const redirectDashboard = () => {
  if (token.value) {
    router.push('/dashboard');
  }
}

onMounted(() => {
  redirectDashboard();
})

</script>

<template>
  <div>
    <h1>Welcome to Our Hospital</h1>
      <p>Your health is our priority. Explore our services and book an appointment today!</p>
      <div class="action-buttons">
        <button @click="patientLogin" class="blue-btn">Patient login</button>
        <button @click="staffLogin" class="blue-btn">Staff login</button>
      </div>
  </div>
</template>

<style scoped>
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
</style>