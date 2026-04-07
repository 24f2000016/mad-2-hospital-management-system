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
    <button @click="home" class="blue-btn">Home</button>
  </div>
</template>

<style scoped>
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