import AdminDashboard from "@/components/Page/Admin/Dashboard.vue";
import PatientDashboard from "@/components/Page/Patient/Dashboard.vue";
import DoctorDashboard from "@/components/Page/Doctor/Dashboard.vue";
import Home from "@/components/Page/General/Home.vue";
import Login from "@/components/Page/Patient/Login.vue";
import Register from "@/components/Page/Patient/Register.vue";
import StaffLogin from "@/components/Page/General/StaffLogin.vue";
import AddDoctor from "@/components/Page/Admin/AddDoctor.vue";
import AddDepartment from "@/components/Page/Admin/AddDepartment.vue";
import AddPatient from "@/components/Page/Admin/AddPatient.vue";
import PatientProfile from "@/components/Page/Patient/Profile.vue";
import AllDoctors from "@/components/Page/Patient/AllDoctors.vue";
import ScheduleAppointment from "@/components/Page/Patient/ScheduleAppointment.vue";
import AdminAllDoctors from "@/components/Page/Admin/AdminAllDoctors.vue";
import AllPatients from "@/components/Page/Admin/AllPatients.vue";
import AllDepartments from "@/components/Page/Admin/AllDepartments.vue";
import AllAppointments from "@/components/Page/Admin/AllAppointments.vue";
import Logout from "@/components/Page/General/Logout.vue";
import AssignedPatients from "@/components/Page/Doctor/AssignedPatients.vue";
import CompleteAppointment from "@/components/Page/Doctor/CompleteAppointment.vue";
import MyAvailability from "@/components/Page/Doctor/MyAvailability.vue";
import PatientMedicalHistory from "@/components/Page/Doctor/PatientMedicalHistory.vue";
import MyMedicalHistory from "@/components/Page/Patient/MyMedicalHistory.vue";
import MyAppointments from "@/components/Page/Patient/MyAppointments.vue";

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
    { path: '/add-doctor', component: AddDoctor },
    { path: '/add-patient', component: AddPatient },
    { path: "/add-department", component:AddDepartment },
    { path: "/dashboard/profile", component:PatientProfile },
    { path: "/dashboard/schedule/doctor", component:AllDoctors },
    { path: "/dashboard/schedule/doctor/appointment", component:ScheduleAppointment },
    { path: "/admin/all-doctors", component:AdminAllDoctors },
    { path: "/admin/all-patients", component:AllPatients },
    { path: "/admin/all-departments", component:AllDepartments },
    { path: "/admin/all-appointments", component:AllAppointments },
    { path: "/logout", component:Logout },
    { path: "/doctor/assigned-patients", component:AssignedPatients },
    { path: "/doctor/complete-appointment", component:CompleteAppointment },
    { path: "/doctor/my-availability", component:MyAvailability },
    { path: "/doctor/patient-medical-history/:patientId", component:PatientMedicalHistory },
    { path: "/patient/my-history", component:MyMedicalHistory },
    { path: "/patient/my-appointments", component:MyAppointments }
  ],
});

export default router;
