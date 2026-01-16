import { runTest } from './utils.js';

runTest('User Login Verification', async (api) => {
    console.log('Testing User Login...');
    try {
        const loginData = {
            username: 'adepojuololade',
            password: 'ololade2020'
        };

        const res = await api.post('/api/users/login/', loginData);
        
        if (res.status === 200 && res.data.token) {
            console.log('✅ Login Successful');
            console.log('User ID:', res.data.user_id);
            console.log('Token:', res.data.token.substring(0, 15) + '...');
        } else {
            throw new Error('Login failed: Invalid response structure');
        }
    } catch (e) {
        if (e.response) {
            console.error('❌ Login Failed with Status:', e.response.status);
            console.error('Response Data:', e.response.data);
        } else {
            throw e;
        }
    }
});
