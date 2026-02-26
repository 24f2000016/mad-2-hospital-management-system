<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const currentUserEmail = ref('Loading...');
const appointments = ref([]);

const todaysAppointments = computed(() => {
  if (!currentUserEmail.value || !appointments.value) return [];
  const today = new Date();
  const yyyy = today.getFullYear();
  const mm = String(today.getMonth() + 1).padStart(2, '0');
  const dd = String(today.getDate()).padStart(2, '0');
  const todayStr = `${yyyy}-${mm}-${dd}`;

  return appointments.value.filter(a => {
    const aDate = (a.appointment_date || '').split(' ')[0];
    const matchesDate = aDate === todayStr;
    // Match by doctor email
    const matchesDoctor = a.doctor_email === currentUserEmail.value;
    return matchesDate && matchesDoctor;
  });
});

const logout = () => {
  localStorage.removeItem('auth_token');
  router.push('/');
};




onMounted(async () => {
  const token = localStorage.getItem('auth_token');
  
  if (!token) {
    currentUserEmail.value = 'No user logged in';
    return;
  }

  try {
    const response = await fetch('http://127.0.0.1:5000/api/current-user-details', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authentication-Token': token
      }
    });

    if (response.ok) {
      const data = await response.json();
      // Extract email from the message or response
      currentUserEmail.value = data.current_user_email || 'Unknown User';
      // after we have user info, load appointments
      await fetchAppointments();
    } else {
      currentUserEmail.value = 'Unable to fetch user data';
    }
  } catch (error) {
    console.error('Error fetching user data:', error);
    currentUserEmail.value = 'Error loading user data';
  }
});







async function fetchAppointments() {
    const token = localStorage.getItem('auth_token');
    try {
        const response = await fetch('http://127.0.0.1:5000/api/appointment', {
            method: 'GET',
            headers: {
                'Authentication-Token': token   
            }
        });
        if (response.ok) {
            const data = await response.json();
            // normalize appointment_date to YYYY-MM-DD so comparisons work
      appointments.value = data.appointments.map(a => ({
        ...a,
        appointment_date: (a.appointment_date || '').split(' ')[0]
      }));
            console.log('Appointments:', appointments.value);
        } else {
            const errorText = await response.text();
            console.error('Failed to fetch appointments:', errorText);
        }
    } catch (error) {
        console.error('Error fetching appointments:', error);
    }
}


</script>


<template>
  <div>
    <h2>Welcome to the Doctor Dashboard!</h2>
    <p><strong>Logged in as:</strong> {{ currentUserEmail }}</p>

    <h3>Today's appointments</h3>

    <div v-if="todaysAppointments.length">
      <ul>
        <li v-for="(appt, idx) in todaysAppointments" :key="appt.id || idx">
          <div>
            <strong>Patient:</strong> {{ appt.patient_name || 'Unknown' }}
          </div>
          <div>
            <strong>Date:</strong> {{ appt.appointment_date }}
            <strong style="margin-left:12px">Time:</strong> {{ appt.appointment_time_slot || 'N/A' }}
            <strong style="margin-left:12px">Status:</strong> {{ appt.status || 'booked' }}
          </div>
        </li>
      </ul>
    </div>
    <div v-else>
      <p>No appointments for today.</p>
    </div>

    <button @click="logout" class="logout-btn">Logout</button>
  </div>
</template>