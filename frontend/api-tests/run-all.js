import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

const files = fs.readdirSync('./api-tests').filter(f => f.endsWith('.js') && f !== 'utils.js' && f !== 'run-all.js');

console.log('--- Starting Automated API Tests ---');

for (const file of files) {
    try {
        execSync(`node api-tests/${file}`, { stdio: 'inherit' });
    } catch (e) {
        console.error(`Test ${file} failed!`);
        process.exit(1);
    }
}

console.log('\n✨ All API tests passed successfully!');
