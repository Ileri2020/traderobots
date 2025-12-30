import axios from 'axios';
import dotenv from 'dotenv';
import path from 'path';

dotenv.config({ path: path.resolve(process.cwd(), '.env') });
dotenv.config({ path: path.resolve(process.cwd(), '../backend/.env') });

const BACKEND_URL = process.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: BACKEND_URL,
    headers: {
        'Content-Type': 'application/json'
    }
});

export const runTest = async (name, testFn) => {
    console.log(`\n🚀 Running Test: ${name}`);
    try {
        await testFn(api);
        console.log(`✅ ${name} Passed`);
    } catch (error) {
        console.error(`❌ ${name} Failed`);
        console.error(error.response?.data || error.message);
        process.exit(1);
    }
};

export default api;
