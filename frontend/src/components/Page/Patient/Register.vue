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
      alert("Registration Successful, please login. (register.vue line 32)");
      // Redirect to dashboard after successful login
      router.push('/login');
    } else {
      alert("Registration Failed (register.vue line 35)");
    }
  } catch (error) {
    console.error(error);
  }
}
</script>

<template>
    <h2>Register</h2>
    <input v-model="email" placeholder="Email" />
    <input v-model="username" placeholder="Username" />
    <input v-model="password" type="password" placeholder="Password" />
    <input v-model="password_confirm" type="password" placeholder="Confirm Password" />
    <button @click="register">Register</button>
</template>