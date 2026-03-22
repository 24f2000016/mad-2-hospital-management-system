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

    <div v-if="upcomingAppointments.length" class="table-wrapper">
      <table class="appointments-table">
        <thead>
          <tr>
            <th>Patient Name</th>
            <th>Date</th>
            <th>Time</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(appt, idx) in upcomingAppointments" :key="appt.id || idx">
            <td>{{ appt.patient_name || 'Unknown' }}</td>
            <td>{{ appt.appointment_date }}</td>
            <td>{{ appt.appointment_time_slot || 'N/A' }}</td>
            <td>
              <span :class="['status-badge', appt.status === 'booked' ? 'booked' : 'completed']">
                {{ appt.status || 'booked' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else>
      <p>No upcoming appointments.</p>
    </div>

    <button @click="logout" class="logout-btn">Logout</button>
  </div>
</template>

<style scoped>
.table-wrapper {
  overflow-x: auto;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.appointments-table {
  width: 100%;
  border-collapse: collapse;
  background-color: white;
}

.appointments-table thead {
  background-color: #1976d2;
  color: white;
}

.appointments-table th {
  padding: 15px;
  text-align: left;
  font-weight: 600;
}

.appointments-table td {
  padding: 12px 15px;
  border-bottom: 1px solid #e0e0e0;
}

.appointments-table tbody tr:hover {
  background-color: #f5f5f5;
}

.appointments-table tbody tr:last-child td {
  border-bottom: none;
}

.status-badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.booked {
  background-color: #e3f2fd;
  color: #1565c0;
}

.status-badge.completed {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.logout-btn {
  padding: 10px 20px;
  background-color: #d32f2f;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-top: 20px;
}

.logout-btn:hover {
  background-color: #b71c1c;
}
</style>