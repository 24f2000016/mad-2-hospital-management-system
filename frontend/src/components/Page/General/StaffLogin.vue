<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const email = ref('');
const password = ref('');
const token = ref(localStorage.getItem('auth_token'));

onMounted(() => {
  if (token.value) {
    router.push('/dashboard');
  }
});

async function currentUserDetails() {
  const token = localStorage.getItem('auth_token');
  try {
    const response = await fetch('http://127.0.0.1:5000/api/current-user-details', {
      method: 'GET',
      headers: { 'Authentication-Token': token }
    });
    if (response.ok) {
      const current_user_details = await response.json();
      console.log('Current User Details:', current_user_details);
      return current_user_details;
    } else {
      console.error('Failed to fetch user details');
      return null;
    }
  } catch (error) {
    console.error('Error fetching user details:', error);
    return null;
  }
}






async function login() {
  try {
    const response = await fetch('http://127.0.0.1:5000/login?include_auth_token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value, password: password.value })
    });

    const data = await response.json();

    if (response.ok) {
      // Flask-Security returns the token in the response body
      token.value = data.response.user.authentication_token;
      localStorage.setItem('auth_token', token.value);
      
      // Fetch user details and redirect based on role
      const userDetails = await currentUserDetails();
      
      if (userDetails && userDetails.current_user_roles) {
        if (userDetails.current_user_roles.includes('admin')) {
          router.push('/admin-dashboard');
        } else if (userDetails.current_user_roles.includes('doctor')) {
          router.push('/doctor-dashboard');
        } else {
          router.push('/dashboard');
        }
      } else {
        // Default redirect if role cannot be determined
        router.push('/dashboard');
      }
    } else {
      alert("Login Failed");
    }
  } catch (error) {
    console.error(error);
  }
}
</script>

<template>
      <h2>Login</h2>
      <input v-model="email" placeholder="Email" />
      <input v-model="password" type="password" placeholder="Password" />
      <button @click="login">Login</button>
</template>