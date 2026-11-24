import fs from 'fs';
import path from 'path';
import {defineConfig} from 'vite';

export default defineConfig(() => {
  return {
    plugins: [
      {
        name: 'stafflog-flask-preview-routes',
        configureServer(server) {
          server.middlewares.use((req, res, next) => {
            const urlPath = (req.url || '').split('?')[0];
            if (urlPath === '/' || urlPath === '/login') {
              const loginHtml = fs.readFileSync(
                path.resolve(__dirname, 'templates/login.html'),
                'utf-8',
              );
              res.statusCode = 200;
              res.setHeader('Content-Type', 'text/html');
              res.end(loginHtml);
              return;
            }
            if (urlPath === '/dashboard' || urlPath === '/dashboard.html') {
              const dashboardHtml = fs.readFileSync(
                path.resolve(__dirname, 'templates/dashboard.html'),
                'utf-8',
              );
              res.statusCode = 200;
              res.setHeader('Content-Type', 'text/html');
              res.end(dashboardHtml);
              return;
            }
            next();
          });
        },
      },
      {
        name: 'copy-static-and-templates',
        apply: 'build',
        closeBundle(error?: Error): void {
          if (error) {
            return;
          }
          const distDir = path.resolve(__dirname, 'dist');
          const staticSrc = path.resolve(__dirname, 'static');
          const staticDist = path.resolve(distDir, 'static');
          const dashboardSrc = path.resolve(__dirname, 'templates/dashboard.html');

          if (fs.existsSync(distDir) && fs.existsSync(staticSrc)) {
            fs.cpSync(staticSrc, staticDist, {recursive: true, force: true});
          }
          if (fs.existsSync(distDir) && fs.existsSync(dashboardSrc)) {
            fs.copyFileSync(dashboardSrc, path.resolve(distDir, 'dashboard.html'));
            const dashboardSubdir = path.resolve(distDir, 'dashboard');
            fs.mkdirSync(dashboardSubdir, {recursive: true});
            fs.copyFileSync(dashboardSrc, path.resolve(dashboardSubdir, 'index.html'));
          }
        },
      },
    ],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),
      },
    },
    server: {
      // HMR is disabled in AI Studio via DISABLE_HMR env var.
      // Do not modify—file watching is disabled to prevent flickering during agent edits.
      hmr: process.env.DISABLE_HMR !== 'true',
      // Disable file watching when DISABLE_HMR is true to save CPU during agent edits.
      watch: process.env.DISABLE_HMR === 'true' ? null : {},
    },
  };
});
