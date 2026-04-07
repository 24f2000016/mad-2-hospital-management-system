<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const email = ref('');
const password = ref('');
const token = ref(localStorage.getItem('auth_token'));
const errorMessage = ref('');

// Redirect to dashboard if already logged in
onMounted(() => {
  if (token.value) {
    router.push('/dashboard');
  }
});

async function login() {
  errorMessage.value = ''; // Clear previous errors
  
  try {
    const response = await fetch('http://127.0.0.1:5000/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value, password: password.value })
    });

    const data = await response.json();

    if (response.ok) {
      // Flask-Security returns the token in the response body or header depending on config
      // Default JSON response usually includes 'response.user.authentication_token'
      token.value = data.response.user.authentication_token;
      localStorage.setItem('auth_token', token.value);
      // Redirect to dashboard after successful login
      router.push('/dashboard');
    } else {
      // Handle error responses (including blacklisted account)
      errorMessage.value = data.error || 'Login failed';
    }
  } catch (error) {
    console.error(error);
    errorMessage.value = 'An error occurred during login. Please try again.';
  }
}

function goToRegister() {
  router.push('/register');
}
</script>


<template>
      <h2>Login</h2>
      <div v-if="errorMessage" style="color: red; margin-bottom: 16px;">
        {{ errorMessage }}
      </div>
      <div class="profile-section">
        <div class="profile-group">
          <label for="email">Email: </label>
          <input v-model="email" id="email" placeholder="Email" />
        </div>
        <div class="profile-group">
          <label for="password">Password: </label>
          <input v-model="password" id="password" type="password" placeholder="Password" />
        </div>
        <div class="action-buttons">
          <button @click="login" class="blue-btn">Login</button>
          <button @click="goToRegister" class="blue-btn">Register</button>
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
  max-width: 490px;
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