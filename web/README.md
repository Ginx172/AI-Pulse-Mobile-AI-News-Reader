# Pulse AI — Web

Next.js 15 PWA web app for Pulse AI — Your AI news heartbeat.

## Quick start

```bash
cd web
npm install
cp .env.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API URL |

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |
| `npm run type-check` | TypeScript type check |

## Tech stack

- **Next.js 15** (App Router, TypeScript strict)
- **React 19**
- **TailwindCSS 3.4+**
- **shadcn/ui** components
- **next-themes** dark/light mode
- **@ducanh2912/next-pwa** PWA + service worker
- **Lucide React** icons
