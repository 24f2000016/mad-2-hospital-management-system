import AdminDashboard from "@/components/Page/Admin/Dashboard.vue";
import PatientDashboard from "@/components/Page/Patient/Dashboard.vue";
import DoctorDashboard from "@/components/Page/Doctor/Dashboard.vue";
import Home from "@/components/Page/General/Home.vue";
import Login from "@/components/Page/Patient/Login.vue";
import Register from "@/components/Page/Patient/Register.vue";
import StaffLogin from "@/components/Page/General/StaffLogin.vue";

import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: Home },
    { path: "/login", component: Login },
    { path: "/register", component: Register },
    { path: "/staff-login", component: StaffLogin },
    { path: "/dashboard", component: PatientDashboard },
    { path: "/doctor-dashboard", component: DoctorDashboard },
    { path: "/admin-dashboard", component: AdminDashboard },
  ],
});

export default router;
