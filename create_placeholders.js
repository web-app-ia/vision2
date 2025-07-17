const fs = require('fs');
const path = require('path');

const appDetailsPath = path.join(__dirname, 'config', 'app_details.json');
const pythonAppsPath = path.join(__dirname, 'python-apps');

const appDetails = JSON.parse(fs.readFileSync(appDetailsPath, 'utf-8'));

for (const appKey in appDetails) {
    const app = appDetails[appKey];
    for (const category of app.categories) {
        const categoryPath = path.join(pythonAppsPath, category);
        if (!fs.existsSync(categoryPath)) {
            fs.mkdirSync(categoryPath, { recursive: true });
        }

        const appPath = path.join(categoryPath, appKey);
        if (!fs.existsSync(appPath)) {
            fs.mkdirSync(appPath, { recursive: true });
        }

        const mainPyPath = path.join(appPath, 'main.py');
        if (!fs.existsSync(mainPyPath)) {
            fs.writeFileSync(mainPyPath, '# Placeholder for ' + app.name);
        }
    }
}
