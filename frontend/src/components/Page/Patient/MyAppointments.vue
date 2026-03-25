<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const appointments = ref([]);
const error = ref(null);

onMounted(async () => {
  const token = localStorage.getItem('auth_token');
  
  if (!token) {
    error.value = 'No authentication token found. Please login first.';
    return;
  }

  try {
    const response = await fetch('http://127.0.0.1:5000/api/patient/my-appointments', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authentication-Token': token
      }
    });

    if (response.ok) {
      const data = await response.json();
      appointments.value = data.appointments || [];
    } else {
      error.value = 'Failed to fetch appointments';
    }
  } catch (err) {
    console.error('Error fetching appointments:', err);
    error.value = 'Error loading appointments';
  }
});

const goBack = () => {
  router.push('/dashboard');
};

const cancelAppointment = async (appointmentId) => {
  if (!confirm('Are you sure you want to cancel this appointment?')) {
    return;
  }

  const token = localStorage.getItem('auth_token');
  try {
    const response = await fetch(`http://127.0.0.1:5000/api/appointment/${appointmentId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authentication-Token': token
      },
      body: JSON.stringify({ status: 'canceled' })
    });

    if (response.ok) {
      // Update the local appointments list
      const appointmentIndex = appointments.value.findIndex(a => a.id === appointmentId);
      if (appointmentIndex !== -1) {
        appointments.value[appointmentIndex].status = 'canceled';
      }
      alert('Appointment canceled successfully');
    } else {
      alert('Failed to cancel appointment');
    }
  } catch (error) {
    console.error('Error canceling appointment:', error);
    alert('Error canceling appointment');
  }
};

const rescheduleAppointment = async (appointmentId) => {
  const confirmed = confirm('We are canceling your current appointment so you can book a fresh appointment');
  
  if (!confirmed) {
    return;
  }

  const token = localStorage.getItem('auth_token');
  try {
    const response = await fetch(`http://127.0.0.1:5000/api/appointment/${appointmentId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authentication-Token': token
      },
      body: JSON.stringify({ status: 'canceled' })
    });

    if (response.ok) {
      // Redirect to schedule page
      router.push('/dashboard/schedule/doctor');
    } else {
      alert('Failed to reschedule appointment');
    }
  } catch (error) {
    console.error('Error rescheduling appointment:', error);
    alert('Error rescheduling appointment');
  }
};
</script>

<template>
  <div class="my-appointments">
    <div class="header">
      <h2>My Appointments</h2>
      <button @click="goBack" class="back-btn">← Back to Dashboard</button>
    </div>

    <div v-if="error" class="error">
      <p>{{ error }}</p>
    </div>

    <div v-else-if="appointments.length === 0" class="no-appointments">
      <p>You have no appointments yet.</p>
    </div>

    <div v-else class="table-wrapper">
      <table class="appointments-table">
        <thead>
          <tr>
            <th>Doctor Name</th>
            <th>Department</th>
            <th>Date</th>
            <th>Time</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="appointment in appointments" :key="appointment.id">
            <td>{{ appointment.doctor_name || 'N/A' }}</td>
            <td>{{ appointment.department || 'N/A' }}</td>
            <td>{{ appointment.appointment_date || 'N/A' }}</td>
            <td>{{ appointment.appointment_time || 'N/A' }}</td>
            <td>
              <span :class="['status-badge', appointment.status]">
                {{ appointment.status }}
              </span>
            </td>
            <td>
              <div class="actions" v-if="appointment.status === 'booked'">
                <button @click="rescheduleAppointment(appointment.id)" class="reschedule-btn">
                  Reschedule
                </button>
                <button @click="cancelAppointment(appointment.id)" class="cancel-btn">
                  Cancel
                </button>
              </div>
              <div v-else class="no-actions">
                <span class="text-muted">No actions</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.my-appointments {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

h2 {
  color: #333;
  margin: 0;
}

.back-btn {
  padding: 10px 20px;
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
}

.back-btn:hover {
  background-color: #5a6268;
}

.error {
  background-color: #ffebee;
  color: #d32f2f;
  padding: 15px;
  border: 1px solid #d32f2f;
  border-radius: 4px;
  text-align: center;
  margin-bottom: 20px;
}

.no-appointments {
  text-align: center;
  padding: 40px;
  background-color: #f5f5f5;
  border-radius: 4px;
  color: #666;
}

.table-wrapper {
  overflow-x: auto;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
  text-transform: capitalize;
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

.actions {
  display: flex;
  gap: 8px;
}

.reschedule-btn {
  padding: 6px 12px;
  background-color: #ff9800;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  transition: background-color 0.2s ease;
}

.reschedule-btn:hover {
  background-color: #f57c00;
}

.cancel-btn {
  padding: 6px 12px;
  background-color: #d32f2f;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  transition: background-color 0.2s ease;
}

.cancel-btn:hover {
  background-color: #b71c1c;
}

.no-actions {
  color: #999;
  font-size: 12px;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }

  .back-btn {
    width: 100%;
  }

  .appointments-table th,
  .appointments-table td {
    padding: 8px 10px;
    font-size: 12px;
  }

  .actions {
    flex-direction: column;
  }

  .reschedule-btn,
  .cancel-btn {
    width: 100%;
  }
}
</style>
