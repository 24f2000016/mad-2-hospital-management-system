<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const token = ref(localStorage.getItem('auth_token'));
const router = useRouter();

// Redirect to dashboard if already logged in
onMounted(() => {
  if (token.value) {
    router.push('/dashboard');
  }
});

</script>

<template>
    <div>
        <h1>Welcome to Our Hospital</h1>
        <p>Your health is our priority. Explore our services and book an appointment today!</p>
        <button @click="$router.push('/login')">Patient login</button>
        <button @click="$router.push('/staff-login')">Staff login</button>
    </div>
</template>