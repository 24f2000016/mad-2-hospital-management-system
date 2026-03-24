<script setup>
import { useRouter } from 'vue-router';
import { onMounted } from 'vue';

const router = useRouter();

const logout = () => {
  localStorage.removeItem('auth_token');
};

const home = () => {
  router.push('/');
};

onMounted(() => {
  logout();
});

</script>

<template>
    <div>
        <h1>Logout</h1>
        <p>You have been successfully logged out.</p>
        <button @click="home">Return to Home</button>
    </div>
</template>