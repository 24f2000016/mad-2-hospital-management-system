<script setup></script>


<template>
  <router-link to="/" style="text-decoration: none;">
    <h2 style="color: orange; font-family: Verdana, Geneva, Tahoma, sans-serif; cursor: pointer;"> New Delhi City Hospital </h2>
  </router-link>
  <div class="ndch-view">
  <router-view></router-view>
  </div>
  <br>

  <footer style="color: gray; font-family: Verdana, Geneva, Tahoma, sans-serif;"> 112, Jeevan Prakash, 25, KG Marg, Atul Grove Road, Janpath, Connaught Place, New Delhi, Delhi 110001 | 1800 0000 | © 2026 New Delhi City Hospital. All rights reserved. </footer>
</template>


<style scoped>
.ndch-view{
  font-family:system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}
</style>