import { runTest } from './utils.js';

runTest('Social & Chat APIs', async (api) => {
    console.log('Testing GET /api/social/groups/');
    try {
        const groupRes = await api.get('/api/social/groups/');
        if (groupRes.status === 200 && Array.isArray(groupRes.data)) {
            console.log(`Successfully fetched ${groupRes.data.length} groups`);
        } else {
            throw new Error('Invalid response for groups');
        }
    } catch (e) {
        if (e.response?.status === 403 || e.response?.status === 401) {
            console.log('Authentication required for Groups (Expected)');
        } else {
            throw e;
        }
    }

    console.log('Testing GET /api/social/messages/ (authenticated usually)');
    try {
        const msgRes = await api.get('/api/social/messages/');
        if (msgRes.status === 200) {
            console.log('Successfully fetched messages');
        }
    } catch (e) {
        if (e.response?.status === 403 || e.response?.status === 401) {
            console.log('Authentication required for Messages (Expected)');
        } else {
            throw e;
        }
    }
});
