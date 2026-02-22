<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const email = ref('');
const password = ref('');
const token = ref(localStorage.getItem('auth_token'));

// Redirect to dashboard if already logged in
onMounted(() => {
  if (token.value) {
    router.push('/dashboard');
  }
});

async function login() {
  try {
    const response = await fetch('http://127.0.0.1:5000/login?include_auth_token', {
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
      alert("Login Failed");
    }
  } catch (error) {
    console.error(error);
  }
}

function goToRegister() {
  router.push('/register');
}
</script>


<template>
      <h2>Login</h2>
      <input v-model="email" placeholder="Email" />
      <input v-model="password" type="password" placeholder="Password" />
      <button @click="login">Login</button>
      <button @click="goToRegister">Register</button>
</template>