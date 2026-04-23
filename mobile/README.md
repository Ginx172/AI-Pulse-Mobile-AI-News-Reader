# AI Pulse — Mobile App

React Native + Expo (TypeScript, expo-router) mobile front-end for AI Pulse.

## Prerequisites

- Node.js ≥ 18
- Expo CLI: `npm install -g expo-cli` (or use `npx expo`)

## Running locally

```bash
cd mobile
npm install
npx expo start
```

Then press:
- `i` to open iOS Simulator
- `a` to open Android Emulator
- Scan the QR code with the **Expo Go** app on your device

## Environment

Create a `.env.local` at the root of `mobile/` (or set `EXPO_PUBLIC_API_URL` in your shell):

```env
EXPO_PUBLIC_API_URL=http://localhost:8000
```

For a physical device, replace `localhost` with your machine's local IP address.

## Project structure

```
mobile/
├── app/
│   ├── _layout.tsx        # Root stack navigator
│   ├── index.tsx          # Feed screen — today's top 25 articles
│   ├── article/
│   │   └── [id].tsx       # Article detail screen
│   └── settings.tsx       # Settings placeholder
├── app.json               # Expo config (name, bundle IDs)
├── package.json
└── tsconfig.json
```

## Building for production

```bash
# Install EAS CLI
npm install -g eas-cli

# Configure EAS
eas build:configure

# Build for iOS / Android
eas build --platform ios
eas build --platform android
```
