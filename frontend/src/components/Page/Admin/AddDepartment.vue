<script setup>
import { onMounted, ref } from 'vue';
const departmentName = ref('');
const departmentDescription = ref('');
const departments = ref([]);



onMounted(fetchDepartments);



async function fetchDepartments() {
    const token = localStorage.getItem('auth_token');

    try {
        const response = await fetch('http://127.0.0.1:5000/api/departments', {
            method: 'GET',
            headers: {
                'Authentication-Token': token
            }
        });

        if (response.ok) {
            const data = await response.json();
            departments.value = data.departments;
            console.log('Departments:', data.departments);
        } else {
            const errorText = await response.text();
            console.error('Failed to fetch departments:', errorText);
        }
    } catch (error) {
        console.error('Error fetching departments:', error);
    }
}


async function addDepartment() {
    const token = localStorage.getItem('auth_token');

    try {
        const response = await fetch('http://127.0.0.1:5000/api/departments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authentication-Token': token
            },
            body: JSON.stringify({ 
                name: departmentName.value, 
                description: departmentDescription.value 
            })
        });

        if (response.ok) {
            alert('Department added successfully');
            departmentName.value = '';
            departmentDescription.value = '';
        } else {
            const errorText = await response.text();
            alert(`Failed to add department: ${errorText}`);
        }
    } catch (error) {
        console.error('Error adding department:', error);
    }
    
    fetchDepartments();}
</script>

    <template>
        <h2>Department list</h2>
        <button @click="fetchDepartments">Refresh Departments</button>
        <table border="1" cellpadding="5" cellspacing="0">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="department in departments" :key="department.id">
                    <td>{{ department.id }}</td>
                    <td>{{ department.name }}</td>
                    <td>{{ department.description }}</td>
                </tr>
            </tbody>
        </table>
        <h2>Add Department</h2>
        <input type="text" v-model="departmentName" placeholder="Department Name">
        <input type="text" v-model="departmentDescription" placeholder="Department Description">
        <button @click="addDepartment">Add Department</button>
    </template>