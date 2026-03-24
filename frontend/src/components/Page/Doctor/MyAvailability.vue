<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const doctorId = ref(null);
const selectedDate = ref('');
const availableSlots = ref([]);
const blockedSlots = ref([]);
const loading = ref(false);
const loadingSlots = ref(false);
const error = ref('');
const successMessage = ref('');
const selectedSlots = ref([]);

onMounted(async () => {
  const token = localStorage.getItem('auth_token');
  if (!token) {
    error.value = 'No authentication token found';
    return;
  }

  try {
    // Get current user details to retrieve doctor info
    const response = await fetch('http://127.0.0.1:5000/api/current-user-details', {
      method: 'GET',
      headers: {
        'Authentication-Token': token
      }
    });

    if (response.ok) {
      const data = await response.json();
      // Fetch all doctors to find current doctor ID
      const doctorsResponse = await fetch('http://127.0.0.1:5000/api/doctor', {
        method: 'GET',
        headers: {
          'Authentication-Token': token
        }
      });
      
      if (doctorsResponse.ok) {
        const doctorsData = await doctorsResponse.json();
        const currentDoctor = doctorsData.doctors.find(d => d.email === data.current_user_email);
        if (currentDoctor) {
          doctorId.value = currentDoctor.id;
          await fetchBlockedSlots();
        }
      }
    } else {
      error.value = 'Failed to get user details';
    }
  } catch (err) {
    error.value = `Error: ${err.message}`;
  }
});

async function fetchAvailableSlots() {
  if (!selectedDate.value) {
    error.value = 'Please select a date';
    return;
  }

  loadingSlots.value = true;
  error.value = '';
  const token = localStorage.getItem('auth_token');

  try {
    const response = await fetch(
      `http://127.0.0.1:5000/api/appointment/available-slots/${doctorId.value}/${selectedDate.value}`,
      {
        method: 'GET',
        headers: {
          'Authentication-Token': token
        }
      }
    );

    if (response.ok) {
      const data = await response.json();
      availableSlots.value = data.available_slots || [];
      selectedSlots.value = [];
    } else {
      error.value = 'Failed to fetch available slots';
    }
  } catch (err) {
    error.value = `Error: ${err.message}`;
  } finally {
    loadingSlots.value = false;
  }
}

async function fetchBlockedSlots() {
  if (!doctorId.value) return;

  const token = localStorage.getItem('auth_token');
  try {
    const response = await fetch(
      `http://127.0.0.1:5000/api/doctor/unavailable-slots/${doctorId.value}`,
      {
        method: 'GET',
        headers: {
          'Authentication-Token': token
        }
      }
    );

    if (response.ok) {
      const data = await response.json();
      blockedSlots.value = data.unavailable_slots || [];
    }
  } catch (err) {
    console.error('Error fetching blocked slots:', err);
  }
}

async function blockSlots() {
  if (selectedSlots.value.length === 0) {
    error.value = 'Please select at least one slot to block';
    return;
  }

  loading.value = true;
  error.value = '';
  successMessage.value = '';
  const token = localStorage.getItem('auth_token');

  try {
    // Block each selected slot
    for (const slot of selectedSlots.value) {
      const response = await fetch(
        'http://127.0.0.1:5000/api/doctor/unavailable-slots',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authentication-Token': token
          },
          body: JSON.stringify({
            start_timestamp: slot.start_timestamp,
            end_timestamp: slot.end_timestamp
          })
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to block slot ${slot.start_time}`);
      }
    }

    successMessage.value = `${selectedSlots.value.length} slot(s) blocked successfully!`;
    selectedSlots.value = [];
    availableSlots.value = [];
    selectedDate.value = '';
    await fetchBlockedSlots();
  } catch (err) {
    error.value = `Error: ${err.message}`;
  } finally {
    loading.value = false;
  }
}

async function unblockSlot(slotId) {
  if (!confirm('Are you sure you want to unblock this slot?')) {
    return;
  }

  const token = localStorage.getItem('auth_token');
  try {
    const response = await fetch(
      `http://127.0.0.1:5000/api/doctor/unavailable-slots/${slotId}`,
      {
        method: 'DELETE',
        headers: {
          'Authentication-Token': token
        }
      }
    );

    if (response.ok) {
      successMessage.value = 'Slot unblocked successfully!';
      await fetchBlockedSlots();
    } else {
      error.value = 'Failed to unblock slot';
    }
  } catch (err) {
    error.value = `Error: ${err.message}`;
  }
}

function toggleSlot(slot) {
  const index = selectedSlots.value.findIndex(s => s.start_timestamp === slot.start_timestamp);
  if (index === -1) {
    selectedSlots.value.push(slot);
  } else {
    selectedSlots.value.splice(index, 1);
  }
}

function goBack() {
  router.push('/doctor-dashboard');
}
</script>

<template>
  <div class="my-availability">
    <div class="header">
      <h2>My Availability</h2>
      <button @click="goBack" class="back-btn">← Back to Dashboard</button>
    </div>

    <div v-if="error" class="error-message">{{ error }}</div>
    <div v-if="successMessage" class="success-message">{{ successMessage }}</div>

    <div class="section">
      <h3>Block Your Time Slots</h3>
      <p>Select a date and choose the time slots during which you are unavailable. Patients won't be able to book these slots.</p>

      <div class="date-picker">
        <label>Select Date:</label>
        <input 
          v-model="selectedDate" 
          type="date"
          @change="fetchAvailableSlots"
          class="date-input"
          :min="new Date().toISOString().split('T')[0]"
        />
      </div>

      <div v-if="loadingSlots" class="loading">Loading available slots...</div>

      <div v-else-if="availableSlots.length > 0" class="slots-section">
        <h4>Available Slots on {{ selectedDate }}</h4>
        <div class="slots-grid">
          <div 
            v-for="slot in availableSlots" 
            :key="slot.start_timestamp"
            class="slot-item"
            :class="{ selected: selectedSlots.some(s => s.start_timestamp === slot.start_timestamp) }"
            @click="toggleSlot(slot)"
          >
            {{ slot.start_time }} - {{ slot.end_time }}
          </div>
        </div>

        <div v-if="selectedSlots.length > 0" class="selected-info">
          <p><strong>Selected {{ selectedSlots.length }} slot(s) to block</strong></p>
          <button @click="blockSlots" :disabled="loading" class="block-btn">
            {{ loading ? 'Blocking...' : 'Block Selected Slots' }}
          </button>
        </div>
      </div>

      <div v-else-if="selectedDate && !loadingSlots" class="no-slots">
        <p>No available slots to block on this date or slots already blocked.</p>
      </div>
    </div>

    <div class="section">
      <h3>Your Blocked Slots</h3>
      <div v-if="blockedSlots.length === 0" class="no-blocked">
        <p>No blocked slots. You are available all the time.</p>
      </div>

      <div v-else class="blocked-slots-list">
        <div 
          v-for="slot in blockedSlots" 
          :key="slot.id"
          class="blocked-slot-item"
        >
          <div class="slot-info">
            <span class="slot-date">{{ slot.date }}</span>
            <span class="slot-time">{{ slot.start_time }} - {{ slot.end_time }}</span>
          </div>
          <button @click="unblockSlot(slot.id)" class="unblock-btn">Unblock</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.my-availability {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header h2 {
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

.error-message {
  background-color: #ffebee;
  color: #c62828;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
  border-left: 4px solid #d32f2f;
}

.success-message {
  background-color: #e8f5e9;
  color: #2e7d32;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
  border-left: 4px solid #388e3c;
}

.section {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
  border-left: 4px solid #1976d2;
}

.section h3 {
  color: #1976d2;
  margin-top: 0;
}

.section p {
  color: #666;
  font-size: 14px;
}

.date-picker {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 20px;
}

.date-picker label {
  font-weight: 600;
  color: #333;
}

.date-input {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  font-family: inherit;
}

.date-input:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 4px rgba(25, 118, 210, 0.2);
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

.slots-section {
  margin-top: 20px;
}

.slots-section h4 {
  color: #333;
  margin-bottom: 15px;
}

.slots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 10px;
  margin-bottom: 20px;
}

.slot-item {
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 4px;
  text-align: center;
  cursor: pointer;
  background-color: white;
  transition: all 0.2s ease;
  font-weight: 500;
  color: #333;
}

.slot-item:hover {
  border-color: #1976d2;
  background-color: #e3f2fd;
}

.slot-item.selected {
  background-color: #1976d2;
  color: white;
  border-color: #1976d2;
}

.no-slots {
  text-align: center;
  padding: 20px;
  color: #999;
  background-color: white;
  border-radius: 4px;
}

.selected-info {
  background-color: white;
  padding: 15px;
  border-radius: 4px;
  border-left: 4px solid #1976d2;
  margin-top: 20px;
}

.selected-info p {
  margin: 0 0 15px 0;
  font-weight: 600;
  color: #1976d2;
}

.block-btn {
  padding: 10px 20px;
  background-color: #388e3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: background-color 0.3s ease;
}

.block-btn:hover:not(:disabled) {
  background-color: #2e7d32;
}

.block-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.no-blocked {
  text-align: center;
  padding: 20px;
  color: #999;
  background-color: white;
  border-radius: 4px;
}

.blocked-slots-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.blocked-slot-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background-color: white;
  border-radius: 4px;
  border-left: 4px solid #d32f2f;
}

.slot-info {
  display: flex;
  gap: 20px;
  align-items: center;
}

.slot-date {
  font-weight: 600;
  color: #333;
  min-width: 100px;
}

.slot-time {
  color: #666;
  font-size: 14px;
}

.unblock-btn {
  padding: 8px 16px;
  background-color: #1976d2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: background-color 0.3s ease;
}

.unblock-btn:hover {
  background-color: #1565c0;
}

@media (max-width: 768px) {
  .slots-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .blocked-slot-item {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }

  .slot-info {
    flex-direction: column;
    gap: 5px;
  }

  .unblock-btn {
    width: 100%;
  }
}
</style>