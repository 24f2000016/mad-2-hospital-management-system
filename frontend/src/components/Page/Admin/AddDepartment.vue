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
    <div class="add-department-container">
        <h2>Departments List</h2>
        <button @click="fetchDepartments" class="refresh-btn">Refresh Departments</button>
        <div class="table-container">
            <table>
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
        </div>

        <h2>Add Department</h2>
        <div class="form-container">
            <input v-model="departmentName" type="text" placeholder="Enter department name">
            <input v-model="departmentDescription" type="text" placeholder="Enter department description">
            <button @click="addDepartment" class="add-btn">Add Department</button>
        </div>
    </div>
</template>

<style scoped>
.add-department-container {
    padding: 20px;
    max-width: 900px;
    margin: 0 auto;
}

h2 {
    color: #333;
    margin-bottom: 20px;
    text-align: center;
    margin-top: 30px;
}

h2:first-child {
    margin-top: 0;
}

.table-container {
    background-color: #f5f5f5;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    margin-bottom: 30px;
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
}

table thead tr {
    background-color: #1976d2;
    color: white;
}

table th {
    padding: 12px;
    text-align: left;
    font-weight: 600;
    border: none;
}

table td {
    padding: 12px;
    border-bottom: 1px solid #ddd;
}

table tbody tr:hover {
    background-color: #f0f0f0;
}

table tbody tr:last-child td {
    border-bottom: none;
}

.refresh-btn {
    padding: 10px 20px;
    background-color: #1976d2;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    transition: background-color 0.3s ease;
    margin-bottom: 15px;
}

.refresh-btn:hover {
    background-color: #1565c0;
}

.form-container {
    display: flex;
    flex-direction: column;
    gap: 15px;
    background-color: #f5f5f5;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

input {
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    font-family: inherit;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

input:focus {
    outline: none;
    border-color: #1976d2;
    box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.add-btn {
    padding: 12px;
    background-color: #1976d2;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.3s ease;
    margin-top: 10px;
}

.add-btn:hover {
    background-color: #1565c0;
}
</style>