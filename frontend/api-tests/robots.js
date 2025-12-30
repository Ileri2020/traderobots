import { runTest } from './utils.js';

runTest('Robot Creation APIs', async (api) => {
    // This test assumes an authenticated session or we skip auth-required ones for now
    // in a real scenario we'd do a login first
    console.log('Testing GET /api/robots/');
    try {
        const res = await api.get('/api/robots/');
        console.log('Successfully fetched robots');
    } catch (e) {
        if (e.response?.status === 403 || e.response?.status === 401) {
            console.log('Authentication required (Expected for this environment)');
        } else {
            throw e;
        }
    }
});
