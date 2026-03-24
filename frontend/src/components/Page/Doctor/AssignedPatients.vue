<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const currentUserEmail = ref('Loading...');
const appointments = ref([]);

const upcomingPatients = computed(() => {
  if (!currentUserEmail.value || !appointments.value) return [];
  const today = new Date();
  const yyyy = today.getFullYear();
  const mm = String(today.getMonth() + 1).padStart(2, '0');
  const dd = String(today.getDate()).padStart(2, '0');
  const todayStr = `${yyyy}-${mm}-${dd}`;

  // Get unique patients with upcoming appointments, showing earliest appointment per patient
  const patientMap = new Map();
  
  appointments.value.forEach(a => {
    const aDate = (a.appointment_start_timestamp || '').split('T')[0];
    const isUpcoming = aDate >= todayStr;
    const matchesDoctor = a.doctor_email === currentUserEmail.value;
    
    if (isUpcoming && matchesDoctor) {
      const key = a.patient_id || a.patient_name;
      if (!patientMap.has(key) || 
          a.appointment_start_timestamp < patientMap.get(key).appointment_start_timestamp) {
        patientMap.set(key, a);
      }
    }
  });

  return Array.from(patientMap.values()).sort((a, b) => {
    return a.appointment_start_timestamp.localeCompare(b.appointment_start_timestamp);
  });
});

const logout = () => {
  router.push('/logout');
};

const backToDashboard = () => {
  router.back();
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
      currentUserEmail.value = data.current_user_email || 'Unknown User';
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
    <h2>Assigned Patients</h2>
    <p><strong>Logged in as:</strong> {{ currentUserEmail }}</p>

    <h3>Upcoming Appointments</h3>

    <div v-if="upcomingPatients.length" class="table-wrapper">
      <table class="appointments-table">
        <thead>
          <tr>
            <th>Patient Name</th>
            <th>Appointment Date</th>
            <th>Time</th>
            <th>Department</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(appt, idx) in upcomingPatients" :key="appt.id || idx">
            <td>{{ appt.patient_name || 'Unknown' }}</td>
            <td>{{ appt.appointment_date }}</td>
            <td>{{ appt.appointment_time_slot || 'N/A' }}</td>
            <td>{{ appt.department || 'N/A' }}</td>
            <td>
              <span :class="['status-badge', appt.status === 'booked' ? 'booked' : appt.status === 'canceled' ? 'canceled' : 'completed']">
                {{ appt.status || 'booked' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else>
      <p>No upcoming appointments with patients.</p>
    </div>

    <div class="button-group">
      <button @click="backToDashboard" class="back-btn">Back to Dashboard</button>
      <button @click="logout" class="logout-btn">Logout</button>
    </div>
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

.status-badge.canceled {
  background-color: #ffebee;
  color: #c62828;
}

.button-group {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.back-btn {
  padding: 10px 20px;
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s ease;
}

.back-btn:hover {
  background-color: #5a6268;
}

.logout-btn {
  padding: 10px 20px;
  background-color: #d32f2f;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s ease;
}

.logout-btn:hover {
  background-color: #b71c1c;
}
</style>