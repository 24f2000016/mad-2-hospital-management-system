<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const currentUserEmail = ref('Loading...');
const appointments = ref([]);

const upcomingAppointments = computed(() => {
  if (!currentUserEmail.value || !appointments.value) return [];
  const today = new Date();
  const yyyy = today.getFullYear();
  const mm = String(today.getMonth() + 1).padStart(2, '0');
  const dd = String(today.getDate()).padStart(2, '0');
  const todayStr = `${yyyy}-${mm}-${dd}`;

  return appointments.value.filter(a => {
    // Extract date from appointment_start_timestamp (ISO format: "2026-03-20T10:30:00")
    const aDate = (a.appointment_start_timestamp || '').split('T')[0];
    // Show appointments from today onwards
    const isUpcoming = aDate >= todayStr;
    // Match by doctor email
    const matchesDoctor = a.doctor_email === currentUserEmail.value;
    return isUpcoming && matchesDoctor;
  }).sort((a, b) => {
    // Sort by appointment date and time
    return a.appointment_start_timestamp.localeCompare(b.appointment_start_timestamp);
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
            // Convert appointment_start_timestamp to readable format
            appointments.value = data.appointments.map(a => ({
                ...a,
                appointment_date: (a.appointment_start_timestamp || '').split('T')[0],
                appointment_time_slot: (a.appointment_start_timestamp || '').split('T')[1]?.substring(0, 5)
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

    <h3>Upcoming appointments</h3>

    <div v-if="upcomingAppointments.length">
      <ul>
        <li v-for="(appt, idx) in upcomingAppointments" :key="appt.id || idx">
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
      <p>No upcoming appointments.</p>
    </div>

    <button @click="logout" class="logout-btn">Logout</button>
  </div>
</template>