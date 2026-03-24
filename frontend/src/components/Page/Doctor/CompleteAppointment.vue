<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

const appointmentId = ref(null);
const appointment = ref(null);
const loading = ref(true);
const submitting = ref(false);
const successMessage = ref('');
const errorMessage = ref('');

const formData = ref({
  diagnosis: '',
  test_done: '',
  prescription: '',
  medicines: '',
  visit_type: 'consultation',
  symptoms: '',
  follow_up_date: '',
  additional_notes: ''
});

const visitTypes = ['consultation', 'follow-up', 'emergency'];

onMounted(async () => {
  appointmentId.value = route.query.id;
  if (!appointmentId.value) {
    errorMessage.value = 'No appointment ID provided';
    loading.value = false;
    return;
  }

  await fetchAppointmentDetails();
});

async function fetchAppointmentDetails() {
  const token = localStorage.getItem('auth_token');
  try {
    const response = await fetch(`http://127.0.0.1:5000/api/appointment/${appointmentId.value}`, {
      method: 'GET',
      headers: {
        'Authentication-Token': token
      }
    });

    if (response.ok) {
      const data = await response.json();
      appointment.value = data;
      console.log('Appointment details:', appointment.value);
    } else {
      errorMessage.value = 'Failed to fetch appointment details';
      console.error('Failed to fetch appointment:', response.status);
    }
  } catch (error) {
    console.error('Error fetching appointment details:', error);
    errorMessage.value = 'Error loading appointment details';
  } finally {
    loading.value = false;
  }
}

async function submitForm() {
  // Validation
  if (!formData.value.diagnosis.trim()) {
    errorMessage.value = 'Diagnosis is required';
    return;
  }

  submitting.value = true;
  successMessage.value = '';
  errorMessage.value = '';

  const token = localStorage.getItem('auth_token');
  try {
    const response = await fetch(`http://127.0.0.1:5000/api/appointments/${appointmentId.value}/complete`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authentication-Token': token
      },
      body: JSON.stringify(formData.value)
    });

    if (response.ok) {
      const data = await response.json();
      successMessage.value = 'Appointment completed successfully!';
      console.log('Completion result:', data);
      
      // Redirect to doctor dashboard after 1.5 seconds
      setTimeout(() => {
        router.push('/doctor-dashboard');
      }, 1500);
    } else {
      const errorData = await response.text();
      errorMessage.value = `Failed to complete appointment: ${errorData}`;
      console.error('Failed response:', errorData);
    }
  } catch (error) {
    console.error('Error submitting form:', error);
    errorMessage.value = `Error: ${error.message}`;
  } finally {
    submitting.value = false;
  }
}

const goBack = () => {
  router.push('/doctor-dashboard');
};
</script>

<template>
  <div class="complete-appointment-container">
    <h2>Complete Appointment</h2>

    <div v-if="loading" class="loading">
      <p>Loading appointment details...</p>
    </div>

    <div v-else-if="errorMessage && !appointment" class="error-message">
      <p>{{ errorMessage }}</p>
      <button @click="goBack" class="back-btn">Back to Dashboard</button>
    </div>

    <div v-else class="form-wrapper">
      <!-- Appointment Info Display -->
      <div class="appointment-info">
        <h3>Appointment Details</h3>
        <div class="info-grid">
          <div class="info-item">
            <span class="label">Patient Name:</span>
            <span class="value">{{ appointment.patient_name || 'Unknown' }}</span>
          </div>
          <div class="info-item">
            <span class="label">Date:</span>
            <span class="value">{{ appointment.appointment_date || appointment.appointment_start_timestamp?.split('T')[0] }}</span>
          </div>
          <div class="info-item">
            <span class="label">Time:</span>
            <span class="value">{{ appointment.appointment_time_slot || appointment.appointment_start_timestamp?.split('T')[1]?.substring(0, 5) }}</span>
          </div>
          <div class="info-item">
            <span class="label">Status:</span>
            <span class="value">{{ appointment.status }}</span>
          </div>
        </div>
      </div>

      <!-- Form Section -->
      <form @submit.prevent="submitForm" class="completion-form">
        <h3>Complete Appointment Form</h3>

        <!-- Visit Type -->
        <div class="form-group">
          <label for="visit-type">Visit Type:</label>
          <select v-model="formData.visit_type" id="visit-type" class="form-input">
            <option v-for="type in visitTypes" :key="type" :value="type">
              {{ type.charAt(0).toUpperCase() + type.slice(1) }}
            </option>
          </select>
        </div>

        <!-- Symptoms -->
        <div class="form-group">
          <label for="symptoms">Symptoms:</label>
          <textarea
            v-model="formData.symptoms"
            id="symptoms"
            class="form-input"
            placeholder="Describe patient symptoms..."
            rows="3"
          ></textarea>
        </div>

        <!-- Diagnosis -->
        <div class="form-group">
          <label for="diagnosis">Diagnosis:</label>
          <textarea
            v-model="formData.diagnosis"
            id="diagnosis"
            class="form-input required-field"
            placeholder="Enter diagnosis (required)..."
            rows="3"
            required
          ></textarea>
          <small class="required-text">*Required field</small>
        </div>

        <!-- Test Done -->
        <div class="form-group">
          <label for="test-done">Tests Performed:</label>
          <textarea
            v-model="formData.test_done"
            id="test-done"
            class="form-input"
            placeholder="List tests performed during appointment..."
            rows="3"
          ></textarea>
        </div>

        <!-- Prescription -->
        <div class="form-group">
          <label for="prescription">Prescription:</label>
          <textarea
            v-model="formData.prescription"
            id="prescription"
            class="form-input"
            placeholder="Enter prescription details..."
            rows="3"
          ></textarea>
        </div>

        <!-- Medicines -->
        <div class="form-group">
          <label for="medicines">Medicines:</label>
          <textarea
            v-model="formData.medicines"
            id="medicines"
            class="form-input"
            placeholder="List medicines prescribed (format: medicine name, dosage, frequency)..."
            rows="3"
          ></textarea>
        </div>

        <!-- Follow-up Date -->
        <div class="form-group">
          <label for="follow-up-date">Follow-up Date (if needed):</label>
          <input
            v-model="formData.follow_up_date"
            id="follow-up-date"
            type="date"
            class="form-input"
          />
        </div>

        <!-- Additional Notes -->
        <div class="form-group">
          <label for="additional-notes">Additional Notes:</label>
          <textarea
            v-model="formData.additional_notes"
            id="additional-notes"
            class="form-input"
            placeholder="Any additional notes or observations..."
            rows="3"
          ></textarea>
        </div>

        <!-- Message Display -->
        <div v-if="successMessage" class="success-message">
          {{ successMessage }}
        </div>
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <!-- Action Buttons -->
        <div class="button-group">
          <button type="submit" class="submit-btn" :disabled="submitting">
            {{ submitting ? 'Submitting...' : 'Complete Appointment' }}
          </button>
          <button type="button" @click="goBack" class="cancel-btn">
            Cancel
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.complete-appointment-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

h2 {
  color: #333;
  margin-bottom: 30px;
  text-align: center;
}

h3 {
  color: #1976d2;
  margin-bottom: 20px;
  border-bottom: 2px solid #1976d2;
  padding-bottom: 10px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
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

.form-wrapper {
  background-color: #f9f9f9;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.appointment-info {
  background-color: white;
  padding: 20px;
  border-radius: 6px;
  margin-bottom: 30px;
  border-left: 4px solid #1976d2;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 15px;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-item .label {
  font-weight: 600;
  color: #666;
  font-size: 12px;
  text-transform: uppercase;
  margin-bottom: 5px;
}

.info-item .value {
  font-size: 16px;
  color: #333;
}

.completion-form {
  background-color: white;
  padding: 20px;
  border-radius: 6px;
}

.form-group {
  margin-bottom: 25px;
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
}

.form-input {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  font-family: inherit;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 0 3px rgba(25, 118, 210, 0.1);
}

.form-input.required-field {
  border-left: 3px solid #d32f2f;
}

.required-text {
  font-size: 12px;
  color: #d32f2f;
  margin-top: 5px;
}

textarea.form-input {
  resize: vertical;
  min-height: 80px;
}

.button-group {
  display: flex;
  gap: 12px;
  margin-top: 30px;
  justify-content: flex-end;
}

.submit-btn {
  padding: 12px 30px;
  background-color: #388e3c;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.submit-btn:hover:not(:disabled) {
  background-color: #2e7d32;
}

.submit-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.cancel-btn {
  padding: 12px 30px;
  background-color: #757575;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.cancel-btn:hover {
  background-color: #616161;
}

.back-btn {
  padding: 10px 20px;
  background-color: #1976d2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-top: 15px;
}

.back-btn:hover {
  background-color: #1565c0;
}
</style>