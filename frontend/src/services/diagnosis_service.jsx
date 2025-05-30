import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL; // Use import.meta.env

export const diagnoseMalaria = async (input) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/malaria`, input);
        return response.data;
    } catch (error) {
        // ... error handling
    }
};