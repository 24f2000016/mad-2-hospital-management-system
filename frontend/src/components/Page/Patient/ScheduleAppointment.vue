<script setup>
import { ref, onMounted, computed } from 'vue'

const selectedDate = ref('')
const doctors = ref([]);
const selectedDoctorId = ref(sessionStorage.getItem('selectedDoctorId'));
const selectedDoctor = computed(() => {
    return doctors.value.find(doc => doc.id === parseInt(selectedDoctorId.value));
});
const appointments = ref([]);


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

onMounted(() => {
    fetchDoctors();
    fetchAppointments();
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

async function bookSlot(slot) {
    if (!selectedDoctor.value) {
        alert('Please select a doctor first.');
        return;
    }
    alert(`Booking slot ${slot} with Dr. ${selectedDoctor.value.full_name} on ${selectedDate.value}`);
    
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
                appointment_date: selectedDate.value,
                appointment_time_slot: slot
            })
        });
        if (response.ok) {
            alert('Appointment booked successfully!');
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
    
    <table v-if="selectedDoctor">
        <thead>
            <tr>
                <th>Time Slot</th>
                <th>Status</th>
                <th>Limit</th>
                <th>Booked</th>
                <th>Available</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>09:00 - 09:30</td>
                <td>Available</td>
                <td>5</td>
                <td>
                    {{ appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '09:00 - 09:30').length }}
                </td>
                <td>{{ 5 - appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '09:00 - 09:30').length }}</td>
                <td><button @click="bookSlot('09:00 - 09:30')" class="btn btn-primary">Book</button></td>
            </tr>
            <tr>
                <td>09:30 - 10:00</td>
                <td>Available</td>
                <td>5</td>
                <td>
                    {{ appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '09:30 - 10:00').length }}
                </td>
                <td>{{ 5 - appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '09:30 - 10:00').length }}</td>
                <td><button @click="bookSlot('09:30 - 10:00')" class="btn btn-primary">Book</button></td>
            </tr>
            <tr>
                <td>10:30 - 11:00</td>
                <td>Available</td>
                <td>5</td>
                <td>
                    {{ appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '10:30 - 11:00').length }}
                </td>
                <td>{{ 5 - appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '10:30 - 11:00').length }}</td>
                <td><button @click="bookSlot('10:30 - 11:00')" class="btn btn-primary">Book</button></td>
            </tr>
            <tr>
                <td>11:00 - 11:30</td>
                <td>Available</td>
                <td>5</td>
                <td>
                    {{ appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '11:00 - 11:30').length }}
                </td>
                <td>{{ 5 - appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '11:00 - 11:30').length }}</td>
                <td><button @click="bookSlot('11:00 - 11:30')" class="btn btn-primary">Book</button></td>
            </tr>
            <tr>
                <td>11:30 - 12:00</td>
                <td>Available</td>
                <td>5</td>
                <td>
                    {{ appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '11:30 - 12:00').length }}
                </td>
                <td>{{ 5 - appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '11:30 - 12:00').length }}</td>
                <td><button @click="bookSlot('11:30 - 12:00')" class="btn btn-primary">Book</button></td>
            </tr>
            <tr>
                <td>12:00 - 12:30</td>
                <td>Available</td>
                <td>5</td>
                <td>
                    {{ appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '12:00 - 12:30').length }}
                </td>
                <td>{{ 5 - appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '12:00 - 12:30').length }}</td>
                <td><button @click="bookSlot('12:00 - 12:30')" class="btn btn-primary">Book</button></td>
            </tr>
            <tr>
                <td>12:30 - 13:00</td>
                <td>Available</td>
                <td>5</td>
                <td>
                    {{ appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '12:30 - 13:00').length }}
                </td>
                <td>{{ 5 - appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '12:30 - 13:00').length }}</td>
                <td><button @click="bookSlot('12:30 - 13:00')" class="btn btn-primary">Book</button></td>
            </tr>
            <tr>
                <td>13:00 - 13:30</td>
                <td>Available</td>
                <td>5</td>
                <td>
                    {{ appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '13:00 - 13:30').length }}
                </td>
                <td>{{ 5 - appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '13:00 - 13:30').length }}</td>
                <td><button @click="bookSlot('13:00 - 13:30')" class="btn btn-primary">Book</button></td>
            </tr>
            <tr>
                <td>13:30 - 14:00</td>
                <td>Available</td>
                <td>5</td>
                <td>
                    {{ appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '13:30 - 14:00').length }}
                </td>
                <td>{{ 5 - appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '13:30 - 14:00').length }}</td>
                <td><button @click="bookSlot('13:30 - 14:00')" class="btn btn-primary">Book</button></td>
            </tr>
            <tr>
                <td>14:00 - 14:30</td>
                <td>Available</td>
                <td>5</td>
                <td>
                    {{ appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '14:00 - 14:30').length }}
                </td>
                <td>{{ 5 - appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '14:00 - 14:30').length }}</td>
                <td><button @click="bookSlot('14:00 - 14:30')" class="btn btn-primary">Book</button></td>
            </tr>
            <tr>
                <td>14:30 - 15:00</td>
                <td>Lunch Break</td>
                <td>0</td>
                <td>0</td>
                <td>0</td>
                <td><button class="btn btn-secondary" disabled>Book</button></td>
            </tr>
            <tr>
                <td>15:00 - 15:30</td>
                <td>Available</td>
                <td>5</td>
                <td>
                    {{ appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '15:00 - 15:30').length }}
                </td>
                <td>{{ 5 - appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '15:00 - 15:30').length }}</td>
                <td><button @click="bookSlot('15:00 - 15:30')" class="btn btn-primary">Book</button></td>
            </tr>
            <tr>
                <td>15:30 - 16:00</td>
                <td>Available</td>
                <td>5</td>
                <td>
                    {{ appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '15:30 - 16:00').length }}
                </td>
                <td>{{ 5 - appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '15:30 - 16:00').length }}</td>
                <td><button @click="bookSlot('15:30 - 16:00')" class="btn btn-primary">Book</button></td>
            </tr>
            <tr>
                <td>16:00 - 16:30</td>
                <td>Available</td>
                <td>5</td>
                <td>
                    {{ appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '13:30 - 14:00').length }}
                </td>
                <td>{{ 5 - appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '16:00 - 16:30').length }}</td>
                <td><button @click="bookSlot('16:00 - 16:30')" class="btn btn-primary">Book</button></td>
            </tr>
            <tr>
                <td>16:30 - 17:00</td>
                <td>Available</td>
                <td>5</td>
                <td>
                    {{ appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '13:30 - 14:00').length }}
                </td>
                <td>{{ 5 - appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '16:30 - 17:00').length }}</td>
                <td><button @click="bookSlot('16:30 - 17:00')" class="btn btn-primary">Book</button></td>
            </tr>
            <tr>
                <td>17:00 - 17:30</td>
                <td>Available</td>
                <td>5</td>
                <td>
                    {{ appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '17:00 - 17:30').length }}
                </td>
                <td>{{ 5 - appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '17:00 - 17:30').length }}</td>
                <td><button @click="bookSlot('17:00 - 17:30')" class="btn btn-primary">Book</button></td>
            </tr>
            <tr>
                <td>17:30 - 18:00</td>
                <td>Available</td>
                <td>5</td>
                <td>
                    {{ appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '17:30 - 18:00').length }}
                </td>
                <td>{{ 5 - appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '17:30 - 18:00').length }}</td>
                <td><button @click="bookSlot('17:30 - 18:00')" class="btn btn-primary">Book</button></td>
            </tr>
            <tr>
                <td>18:00 - 18:30</td>
                <td>Available</td>
                <td>5</td>
                <td>
                    {{ appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '18:00 - 18:30').length }}
                </td>
                <td>{{ 5 - appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '18:00 - 18:30').length }}</td>
                <td><button @click="bookSlot('18:00 - 18:30')" class="btn btn-primary">Book</button></td>
            </tr>
            <tr>
                <td>18:30 - 19:00</td>
                <td>Available</td>
                <td>5</td>
                <td>
                    {{ appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '18:30 - 19:00').length }}
                </td>
                <td>{{ 5 - appointments.filter(a => a.doctor_id === selectedDoctor.id && a.appointment_date == selectedDate && a.appointment_time_slot == '18:30 - 19:00').length }}</td>
                <td><button @click="bookSlot('18:30 - 19:00')" class="btn btn-primary">Book</button></td>
            </tr>
        </tbody>
    </table>
    <div v-else style="margin-top:10px;">Please select a doctor to view and book slots.</div>
</template>