import { runTest } from './utils.js';

runTest('Home Page APIs (Posts)', async (api) => {
    // 1. Create a dummy user is usually handled via backend management commands in CI
    // But here we'll try to use a test login if possible
    console.log('Testing GET /api/social/posts/');
    try {
        const res = await api.get('/api/social/posts/');
        if (res.status === 200 && Array.isArray(res.data)) {
            console.log('Successfully fetched posts');
        } else {
            throw new Error('Invalid response for posts');
        }
    } catch (e) {
        if (e.response?.status === 403 || e.response?.status === 401) {
            console.log('Authentication required (Allowed)');
        } else {
            throw e;
        }
    }
});
