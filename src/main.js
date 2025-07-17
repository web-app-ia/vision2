const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn, exec } = require('child_process');

let mainWindow;
let runningProcesses = new Map();

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        icon: path.join(__dirname, '../assets/icon.ico'),
        title: 'Computer Vision Applications',
        show: false
    });

    mainWindow.loadFile(path.join(__dirname, 'index.html'));

    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
    });

    // Ouvrir DevTools en mode développement
    if (process.env.NODE_ENV === 'development') {
        mainWindow.webContents.openDevTools();
    }

    mainWindow.on('closed', () => {
        // Arrêter tous les processus Python en cours
        for (const [appName, process] of runningProcesses) {
            if (process && !process.killed) {
                process.kill();
            }
        }
        runningProcesses.clear();
        mainWindow = null;
    });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

// IPC Handlers
ipcMain.handle('get-python-apps', () => {
    const appsDir = path.join(__dirname, '../python-apps');
    const categoriesPath = path.join(__dirname, '../config/categories.json');
    const apps = [];
    let categories = {};

    try {
        // Charger les catégories depuis le fichier JSON
        if (fs.existsSync(categoriesPath)) {
            const categoriesFile = fs.readFileSync(categoriesPath);
            categories = JSON.parse(categoriesFile).categories;
        }

        // Scanner les applications et les associer aux catégories
        const categoryKeys = Object.keys(categories);
        for (const category of categoryKeys) {
            const categoryPath = path.join(appsDir, category);
            if (fs.existsSync(categoryPath) && fs.statSync(categoryPath).isDirectory()) {
                const categoryApps = fs.readdirSync(categoryPath);
                
                for (const appName of categoryApps) {
                    const appPath = path.join(categoryPath, appName);
                    if (fs.statSync(appPath).isDirectory()) {
                        const mainPyPath = path.join(appPath, 'main.py');
                        const batchPath = path.join(appPath, 'launch.bat');
                        
                        if (fs.existsSync(mainPyPath)) {
                            apps.push({
                                name: appName,
                                category: category,
                                path: appPath,
                                mainPy: mainPyPath,
                                batchFile: batchPath,
                                hasLauncher: fs.existsSync(batchPath)
                            });
                        }
                    }
                }
            }
        }
    } catch (error) {
        console.error('Error reading Python apps:', error);
    }
    
    // Retourner les applications et les catégories
    return { apps, categories };
});

ipcMain.handle('launch-python-app', async (event, appInfo) => {
    try {
        // Arrêter le processus précédent s'il existe
        if (runningProcesses.has(appInfo.name)) {
            const oldProcess = runningProcesses.get(appInfo.name);
            if (oldProcess && !oldProcess.killed) {
                oldProcess.kill();
            }
        }

        let process;
        
        if (appInfo.hasLauncher && fs.existsSync(appInfo.batchFile)) {
            // Lancer via le fichier batch
            process = spawn('cmd', ['/c', appInfo.batchFile], {
                cwd: appInfo.path,
                stdio: 'ignore',
                detached: true,
                windowsHide: true
            });
        } else {
            // Lancer directement Python
            process = spawn('python', [appInfo.mainPy], {
                cwd: appInfo.path,
                stdio: 'ignore',
                detached: true,
                windowsHide: true
            });
        }

        runningProcesses.set(appInfo.name, process);

        process.on('error', (error) => {
            console.error(`Error launching ${appInfo.name}:`, error);
            runningProcesses.delete(appInfo.name);
        });

        process.on('exit', (code) => {
            console.log(`${appInfo.name} exited with code ${code}`);
            runningProcesses.delete(appInfo.name);
        });

        return { success: true, message: `${appInfo.name} lancé avec succès` };
    } catch (error) {
        console.error('Error launching app:', error);
        return { success: false, message: error.message };
    }
});

ipcMain.handle('stop-python-app', async (event, appName) => {
    try {
        if (runningProcesses.has(appName)) {
            const process = runningProcesses.get(appName);
            if (process && !process.killed) {
                process.kill();
                runningProcesses.delete(appName);
                return { success: true, message: `${appName} arrêté` };
            }
        }
        return { success: false, message: 'Processus non trouvé' };
    } catch (error) {
        return { success: false, message: error.message };
    }
});

ipcMain.handle('get-running-apps', () => {
    return Array.from(runningProcesses.keys());
});

ipcMain.handle('open-external', async (event, url) => {
    try {
        await shell.openExternal(url);
        return { success: true };
    } catch (error) {
        return { success: false, message: error.message };
    }
});

ipcMain.handle('show-message', async (event, options) => {
    const result = await dialog.showMessageBox(mainWindow, options);
    return result;
});
