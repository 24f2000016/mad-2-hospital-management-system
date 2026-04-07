<script setup>
import { ref, onMounted } from 'vue';

const departments = ref([]);
const loading = ref(true);
const error = ref(null);

function goBack() {
    window.location.href = '/admin-dashboard';
}

onMounted(() => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
        error.value = "No authentication token found. Please login first.";
        loading.value = false;
        return;
    }

    fetch('http://localhost:5000/api/admin-dashboard', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authentication-Token': token
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            departments.value = data.departments || [];
            loading.value = false;
        })
        .catch(err => {
            error.value = err.message || "Error fetching departments data";
            loading.value = false;
        });
});
</script>

<template>
    <div class="all-departments">
        <div class="header">
            <h2>All Departments</h2>
            <button @click="goBack" class="back-btn">← Back</button>
        </div>

        <div v-if="loading" class="loading">
            <p>Loading departments...</p>
        </div>

        <div v-else-if="error" class="error">
            <p>{{ error }}</p>
        </div>

        <div v-else-if="departments.length === 0" class="no-departments">
            <p>No departments created yet.</p>
        </div>

        <div v-else class="table-wrapper">
            <table class="departments-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Department Name</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="department in departments" :key="department.id">
                        <td>{{ department.id }}</td>
                        <td>{{ department.name || 'N/A' }}</td>
                        <td>{{ department.description || 'N/A' }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<style scoped>
.all-departments {
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

.loading, .error {
    text-align: center;
    padding: 40px 20px;
    font-size: 16px;
}

.error {
    color: #d32f2f;
    background-color: #ffebee;
    border: 1px solid #d32f2f;
    border-radius: 4px;
}

.no-departments {
    text-align: center;
    padding: 40px;
    color: #666;
    font-size: 16px;
    background-color: #f5f5f5;
    border-radius: 4px;
}

.table-wrapper {
    overflow-x: auto;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.departments-table {
    width: 100%;
    border-collapse: collapse;
    background-color: white;
}

.departments-table thead {
    background-color: #1976d2;
    color: white;
}

.departments-table th {
    padding: 15px;
    text-align: left;
    font-weight: 600;
}

.departments-table td {
    padding: 12px 15px;
    border-bottom: 1px solid #e0e0e0;
}

.departments-table tbody tr:hover {
    background-color: #f5f5f5;
}

.departments-table tbody tr:last-child td {
    border-bottom: none;
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

    .departments-table th,
    .departments-table td {
        padding: 8px 10px;
        font-size: 14px;
    }
}
</style>
