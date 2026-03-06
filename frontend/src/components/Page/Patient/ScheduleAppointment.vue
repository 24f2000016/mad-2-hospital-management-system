<script setup>
import { ref, onMounted, computed } from 'vue'

const selectedDate = ref('')
const doctors = ref([]);
const selectedDoctorId = ref(sessionStorage.getItem('selectedDoctorId'));
const selectedDoctor = computed(() => {
    return doctors.value.find(doc => doc.id === parseInt(selectedDoctorId.value));
});
const availableSlots = ref([]);
const selectedSlot = ref(null);
const loadingSlots = ref(false);


const pad = (n) => String(n).padStart(2, '0')
const toYMD = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`

const today = new Date()
const minDate = toYMD(today)
const maxDate = toYMD(new Date(today.getFullYear(), today.getMonth(), today.getDate() + 20))

// default to today's date
selectedDate.value = minDate

async function fetchDoctors() {
    const token = localStorage.getItem('auth_token');
    try {
        const response = await fetch('http://127.0.0.1:5000/api/doctor', {
            method: 'GET',
            headers: {
                'Authentication-Token': token   
            }
        });
        if (response.ok) {
            const data = await response.json();
            doctors.value = data.doctors;
            console.log('Doctors:', data.doctors);
        } else {
            const errorText = await response.text();
            console.error('Failed to fetch doctors:', errorText);
        }
    } catch (error) {
        console.error('Error fetching doctors:', error);
    }
}

async function fetchAvailableSlots() {
    if (!selectedDoctor.value || !selectedDate.value) {
        availableSlots.value = [];
        selectedSlot.value = null;
        return;
    }

    loadingSlots.value = true;
    const token = localStorage.getItem('auth_token');
    try {
        const response = await fetch(
            `http://127.0.0.1:5000/api/appointment/available-slots/${selectedDoctor.value.id}/${selectedDate.value}`,
            {
                method: 'GET',
                headers: {
                    'Authentication-Token': token   
                }
            }
        );
        if (response.ok) {
            const data = await response.json();
            availableSlots.value = data.available_slots;
            selectedSlot.value = null;
            console.log('Available slots:', data.available_slots);
        } else {
            const errorText = await response.text();
            console.error('Failed to fetch available slots:', errorText);
            availableSlots.value = [];
            selectedSlot.value = null;
        }
    } catch (error) {
        console.error('Error fetching available slots:', error);
        availableSlots.value = [];
        selectedSlot.value = null;
    } finally {
        loadingSlots.value = false;
    }
}

onMounted(() => {
    fetchDoctors();
});

// Watch for doctor or date changes
import { watch } from 'vue'
watch([selectedDoctorId, selectedDate], () => {
    fetchAvailableSlots();
});

async function bookSlot() {
    if (!selectedDoctor.value) {
        alert('Please select a doctor first.');
        return;
    }
    
    if (!selectedSlot.value) {
        alert('Please select a time slot.');
        return;
    }
    
    const slot = JSON.parse(selectedSlot.value);
    const confirmBook = confirm(`Book appointment with Dr. ${selectedDoctor.value.full_name} on ${selectedDate.value} from ${slot.start_time} to ${slot.end_time}?`);
    if (!confirmBook) return;
    
    const token = localStorage.getItem('auth_token');
    try {
        const response = await fetch('http://127.0.0.1:5000/api/appointment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authentication-Token': token
            },
            body: JSON.stringify({
                doctor_id: selectedDoctor.value.id,
                appointment_start_timestamp: slot.start_timestamp,
                appointment_end_timestamp: slot.end_timestamp
            })
        });
        if (response.ok) {
            alert('Appointment booked successfully!');
            await fetchAvailableSlots();
        } else {
            const errorText = await response.text();
            alert(`Failed to book appointment: ${errorText}`);
        }
    } catch (error) {
        console.error('Error booking appointment:', error);
        alert('Error booking appointment.');
    }
}

</script>

<template>
    <div v-if="selectedDoctor" style="margin-top: 20px; padding: 15px; border: 1px solid #ccc; border-radius: 4px;">
        <h4>Selected Doctor</h4>
        <p><strong>Name:</strong> Dr. {{ selectedDoctor.full_name }}</p>
        <p><strong>Department:</strong> {{ selectedDoctor.department }}</p>
        <p><strong>ID:</strong> {{ selectedDoctor.id }}</p>
    </div>

    <h2>Schedule Appointment</h2>

    <label for="appointment-date">Select date (next 20 days):</label>
    <input
        id="appointment-date"
        type="date"
        v-model="selectedDate"
        :min="minDate"
        :max="maxDate"
    />
    <p v-if="selectedDate">Selected: {{ selectedDate }}</p>

    <div v-if="selectedDoctor && !loadingSlots && availableSlots.length > 0" style="margin-top: 20px;">
        <label for="appointment-slot">Select time slot:</label>
        <select 
            id="appointment-slot" 
            v-model="selectedSlot"
            style="padding: 8px; font-size: 16px; margin: 10px 0;"
        >
            <option value="">-- Choose a time slot --</option>
            <option 
                v-for="slot in availableSlots" 
                :key="`${slot.start_time}-${slot.end_time}`"
                :value="JSON.stringify(slot)"
            >
                {{ slot.start_time }} - {{ slot.end_time }}
            </option>
        </select>
        
        <div style="margin-top: 15px;">
            <button 
                @click="bookSlot"
                class="btn btn-primary"
                :disabled="!selectedSlot"
            >
                Book Appointment
            </button>
        </div>
    </div>
    
    <div v-else-if="loadingSlots" style="margin-top: 20px; padding: 15px; text-align: center;">
        Loading available slots...
    </div>
    
    <div v-else-if="!selectedDoctor" style="margin-top: 20px; padding: 15px;">
        Please select a doctor to view available slots.
    </div>
    
    <div v-else style="margin-top: 20px; padding: 15px;">
        No available slots for the selected date.
    </div>
</template>