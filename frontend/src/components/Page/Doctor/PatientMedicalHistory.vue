<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

const patientId = ref(route.params.patientId);
const loading = ref(true);
const error = ref('');
const patientInfo = ref(null);
const medicalHistory = ref([]);

onMounted(async () => {
  await fetchMedicalHistory();
});

async function fetchMedicalHistory() {
  const token = localStorage.getItem('auth_token');
  
  if (!token) {
    error.value = 'No authentication token found. Please login again.';
    loading.value = false;
    return;
  }

  try {
    const response = await fetch(`http://127.0.0.1:5000/api/patient/${patientId.value}/medical-history`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authentication-Token': token
      }
    });

    if (response.ok) {
      const data = await response.json();
      patientInfo.value = {
        name: data.patient_name,
        dob: data.dob,
        sex: data.sex,
        contact: data.contact_number
      };
      medicalHistory.value = data.medical_history || [];
    } else if (response.status === 403) {
      error.value = 'You do not have permission to view this patient\'s medical history.';
    } else if (response.status === 404) {
      error.value = 'Patient not found.';
    } else {
      error.value = 'Failed to fetch medical history.';
    }
  } catch (err) {
    console.error('Error fetching medical history:', err);
    error.value = 'Error loading medical history. Please try again.';
  } finally {
    loading.value = false;
  }
}

const goBack = () => {
  router.back();
};

const formatDate = (dateStr) => {
  if (!dateStr || dateStr === 'N/A') return 'N/A';
  const date = new Date(dateStr + 'T00:00:00');
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
};

const getFieldDisplay = (value) => {
  return (value && value !== 'N/A' && value.trim()) ? value : 'Not recorded';
};
</script>

<template>
  <div class="medical-history-container">
    <div class="header">
      <button @click="goBack" class="back-btn">← Back</button>
      <h2>Patient Medical History</h2>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading">
      Loading medical history...
    </div>

    <!-- Patient Info -->
    <div v-else-if="patientInfo && !error" class="patient-info-card">
      <div class="info-section">
        <h3>{{ patientInfo.name }}</h3>
        <div class="info-grid">
          <div class="info-item">
            <span class="label">Date of Birth:</span>
            <span class="value">{{ formatDate(patientInfo.dob) }}</span>
          </div>
          <div class="info-item">
            <span class="label">Sex:</span>
            <span class="value">{{ patientInfo.sex }}</span>
          </div>
          <div class="info-item">
            <span class="label">Contact:</span>
            <span class="value">{{ patientInfo.contact }}</span>
          </div>
          <div class="info-item">
            <span class="label">Total Completed Appointments:</span>
            <span class="value">{{ medicalHistory.length }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Medical History Timeline -->
    <div v-if="!loading && !error" class="history-container">
      <div v-if="medicalHistory.length === 0" class="no-history">
        <p>No completed appointments found.</p>
      </div>

      <div v-else class="timeline">
        <div v-for="(entry, idx) in medicalHistory" :key="entry.appointment_id || idx" class="timeline-card">
          <div class="card-header">
            <div class="appointment-info">
              <h4>{{ entry.doctor_name }} - {{ entry.department }}</h4>
              <p class="appointment-date">
                📅 {{ formatDate(entry.appointment_date) }} at {{ entry.appointment_time || 'N/A' }}
              </p>
            </div>
            <span class="card-number">{{ idx + 1 }}</span>
          </div>

          <div class="card-body">
            <!-- Visit Type -->
            <div class="detail-row">
              <span class="detail-label">Visit Type:</span>
              <span class="detail-value">{{ getFieldDisplay(entry.visit_type) }}</span>
            </div>

            <!-- Symptoms -->
            <div class="detail-row">
              <span class="detail-label">Symptoms:</span>
              <span class="detail-value">{{ getFieldDisplay(entry.symptoms) }}</span>
            </div>

            <!-- Diagnosis -->
            <div class="detail-row diagnosis-row">
              <span class="detail-label">Diagnosis:</span>
              <span class="detail-value diagnosis-text">{{ getFieldDisplay(entry.diagnosis) }}</span>
            </div>

            <!-- Tests -->
            <div class="detail-row">
              <span class="detail-label">Tests Done:</span>
              <span class="detail-value">{{ getFieldDisplay(entry.tests) }}</span>
            </div>

            <!-- Prescription -->
            <div class="detail-row">
              <span class="detail-label">Prescription:</span>
              <span class="detail-value">{{ getFieldDisplay(entry.prescription) }}</span>
            </div>

            <!-- Medicines -->
            <div class="detail-row">
              <span class="detail-label">Medicines:</span>
              <span class="detail-value">{{ getFieldDisplay(entry.medicines) }}</span>
            </div>

            <!-- Additional Notes -->
            <div class="detail-row">
              <span class="detail-label">Additional Notes:</span>
              <span class="detail-value">{{ getFieldDisplay(entry.additional_notes) }}</span>
            </div>

            <!-- Follow-up Date -->
            <div v-if="entry.follow_up_date" class="detail-row follow-up-row">
              <span class="detail-label">Follow-up Date:</span>
              <span class="detail-value follow-up-date">{{ formatDate(entry.follow_up_date) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.medical-history-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 30px;
}

.back-btn {
  padding: 8px 16px;
  background-color: #1976d2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s ease;
}

.back-btn:hover {
  background-color: #1565c0;
}

h2 {
  color: #333;
  margin: 0;
  flex: 1;
}

.error-message {
  background-color: #ffebee;
  border-left: 4px solid #d32f2f;
  padding: 16px;
  border-radius: 4px;
  color: #c62828;
  margin-bottom: 20px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
  font-size: 16px;
}

.patient-info-card {
  background-color: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 30px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.info-section h3 {
  color: #1976d2;
  margin: 0 0 20px 0;
  font-size: 24px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item .label {
  font-weight: 600;
  color: #666;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-item .value {
  color: #333;
  font-size: 14px;
}

.history-container {
  margin-top: 30px;
}

.no-history {
  background-color: white;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  color: #999;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.timeline {
  position: relative;
  padding-left: 10px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: linear-gradient(to bottom, #1976d2, #42a5f5);
}

.timeline-card {
  background-color: white;
  border-radius: 8px;
  margin-bottom: 24px;
  margin-left: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}

.timeline-card::before {
  content: '';
  position: absolute;
  width: 16px;
  height: 16px;
  background-color: #1976d2;
  border: 3px solid white;
  border-radius: 50%;
  top: 24px;
  left: -40px;
  box-shadow: 0 0 0 3px #1976d2;
}

.timeline-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.card-header {
  background: linear-gradient(135deg, #1976d2 0%, #42a5f5 100%);
  color: white;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.appointment-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
}

.appointment-date {
  margin: 0;
  font-size: 13px;
  opacity: 0.9;
}

.card-number {
  background-color: rgba(255, 255, 255, 0.2);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.card-body {
  padding: 20px;
}

.detail-row {
  display: grid;
  grid-template-columns: 150px 1fr;
  gap: 16px;
  margin-bottom: 16px;
  align-items: flex-start;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 12px;
}

.detail-row:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.detail-label {
  font-weight: 600;
  color: #1976d2;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-value {
  color: #333;
  line-height: 1.5;
  word-wrap: break-word;
}

.diagnosis-row .detail-value.diagnosis-text {
  background-color: #e3f2fd;
  padding: 8px 12px;
  border-radius: 4px;
  border-left: 3px solid #1976d2;
  font-weight: 500;
}

.follow-up-row .detail-value.follow-up-date {
  background-color: #e8f5e9;
  padding: 8px 12px;
  border-radius: 4px;
  border-left: 3px solid #4caf50;
  font-weight: 500;
  color: #2e7d32;
}

@media (max-width: 768px) {
  .medical-history-container {
    padding: 12px;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .detail-row {
    grid-template-columns: 1fr;
    gap: 4px;
  }

  .detail-label {
    font-size: 12px;
  }

  .detail-value {
    font-size: 14px;
  }

  .timeline-card {
    margin-left: 20px;
  }

  .timeline-card::before {
    left: -30px;
  }
}
</style>
