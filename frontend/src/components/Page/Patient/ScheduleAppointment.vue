<script setup>
import { ref, onMounted, computed } from 'vue'

const selectedDate = ref('')
const doctors = ref([]);
const selectedDoctorId = ref(sessionStorage.getItem('selectedDoctorId'));
const selectedDoctor = computed(() => {
    return doctors.value.find(doc => doc.id === parseInt(selectedDoctorId.value));
});
const availableSlots = ref([]);
const appointments = ref([]);
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
            console.log('Available slots:', data.available_slots);
        } else {
            const errorText = await response.text();
            console.error('Failed to fetch available slots:', errorText);
            availableSlots.value = [];
        }
    } catch (error) {
        console.error('Error fetching available slots:', error);
        availableSlots.value = [];
    } finally {
        loadingSlots.value = false;
    }
}

onMounted(() => {
    fetchDoctors();
    fetchAppointments();
});

// Watch for doctor or date changes
import { watch } from 'vue'
watch([selectedDoctorId, selectedDate], () => {
    fetchAvailableSlots();
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
            appointments.value = data.appointments;
            console.log('Appointments:', appointments.value);
        } else {
            const errorText = await response.text();
            console.error('Failed to fetch appointments:', errorText);
        }
    } catch (error) {
        console.error('Error fetching appointments:', error);
    }
}

async function bookSlot(slot) {
    if (!selectedDoctor.value) {
        alert('Please select a doctor first.');
        return;
    }
    
    const confirmBook = confirm(`Book slot ${slot.start_time} - ${slot.end_time} with Dr. ${selectedDoctor.value.full_name} on ${selectedDate.value}?`);
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
            await fetchAppointments();
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

    <h3>Available Slots:</h3>
    
    <div v-if="loadingSlots" style="padding: 15px; text-align: center;">
        Loading available slots...
    </div>
    
    <table v-else-if="selectedDoctor && availableSlots.length > 0">
        <thead>
            <tr>
                <th>Time Slot</th>
                <th>Status</th>
                <th>Capacity</th>
                <th>Booked</th>
                <th>Available</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="slot in availableSlots" :key="`${slot.start_time}-${slot.end_time}`">
                <td>{{ slot.start_time }} - {{ slot.end_time }}</td>
                <td>{{ slot.available > 0 ? 'Available' : slot.booked > 0 ? 'Full' : 'Available' }}</td>
                <td>5</td>
                <td>{{ slot.booked }}</td>
                <td>{{ slot.available }}</td>
                <td>
                    <button 
                        @click="bookSlot(slot)" 
                        class="btn btn-primary"
                        :disabled="slot.available === 0"
                    >
                        {{ slot.available > 0 ? 'Book' : 'Full' }}
                    </button>
                </td>
            </tr>
        </tbody>
    </table>
    <div v-else-if="!selectedDoctor" style="margin-top:10px;">Please select a doctor to view and book slots.</div>
    <div v-else style="margin-top:10px;">No available slots for the selected date.</div>
</template>