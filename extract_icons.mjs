import fs from 'fs';
const icons = JSON.parse(fs.readFileSync('node_modules/@iconify-json/streamline-plump/icons.json', 'utf8'));
const keys = ['cog', 'task-list-add', 'task-list-edit'];

let output = '';
keys.forEach(key => {
    if (icons.icons[key]) {
        output += `KEY: ${key}\n`;
        output += icons.icons[key].body + '\n';
        output += '---\n';
    } else {
        const matches = Object.keys(icons.icons).filter(k => k.includes('task-list'));
        console.log(`Matches for task-list:`, matches.slice(0, 5));
    }
});
fs.writeFileSync('icons_data_2.txt', output);
