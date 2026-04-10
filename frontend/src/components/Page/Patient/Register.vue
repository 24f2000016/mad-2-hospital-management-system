<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const email = ref('');
const password = ref('');
const password_confirm = ref('');
const username = ref('');
const token = ref(localStorage.getItem('auth_token'));

// Redirect to dashboard if already logged in
onMounted(() => {
  if (token.value) {
    router.push('/dashboard');
  }
});

async function register() {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        email: email.value, 
        password: password.value, 
        password_confirm: password_confirm.value, 
        username: username.value 
      })
    });

    const data = await response.json();

    alert(data.message);

    if (response.ok) {
      alert("Registration Successful, please login.");
      // Redirect to dashboard after successful login
      router.push('/login');
    } else {
      alert("Registration Failed");
    }
  } catch (error) {
    console.error(error);
  }
}
</script>

<template>
  <div class="profile-group">
    <h2>Register</h2>
  </div>
  <div class="profile-section">
    <div class="profile-group">
      <label for="email">Email: </label>
      <input v-model="email" placeholder="Email" id="email" />
    </div>
    <div class="profile-group">
      <label for="username">Username: </label>
      <input v-model="username" placeholder="Username" id="username" />
    </div>
    <div class="profile-group">
      <label for="password">Set password: </label>
      <input v-model="password" type="password" placeholder="Password" id="password" />
    </div>
    <div class="profile-group">
      <label for="password_confirm">Confirm password: </label>
      <input v-model="password_confirm" type="password" placeholder="Confirm Password" />
    </div>
    <div>
      <button @click="register" class="blue-btn">Register</button>
    </div>
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
  max-width: 480px;
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

.action-buttons {
    display: flex;
    gap: 10px;
    margin-top: 20px;
    justify-content: flex;
}
</style>