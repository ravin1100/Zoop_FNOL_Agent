# ZOOP FNOL Frontend

A Next.js frontend application for the ZOOP FNOL (First Notice of Loss) insurance claim processing system.

## Features

- **Dashboard**: Real-time metrics and analytics
- **Claim Submission**: Interactive form with live processing updates
- **Server-Sent Events**: Real-time claim processing status
- **Responsive Design**: Mobile-friendly interface with Tailwind CSS

## Setup & Installation

1. **Navigate to frontend directory**:

   ```bash
   cd frontend
   ```

2. **Install dependencies**:

   ```bash
   npm install
   ```

3. **Start development server**:

   ```bash
   npm run dev
   ```

4. **Access the application**:
   - Open http://localhost:3000 in your browser

## Configuration

The application uses Next.js API rewrites to proxy requests to the backend:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000 (auto-proxied via `/api/*`)

## Pages

### Dashboard (`/`)

- Total claims overview
- Risk and priority distributions
- Recent activity table
- Key performance metrics

### Submit Claim (`/submit-claim`)

- Comprehensive claim form
- Real-time processing status
- Server-sent event updates
- Success confirmation

## Architecture

```
src/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Dashboard page
│   └── submit-claim/
│       └── page.tsx       # Claim form page
├── components/            # React components
│   ├── Dashboard.tsx      # Dashboard metrics
│   ├── ClaimForm.tsx      # Claim submission form
│   └── Navigation.tsx     # Navigation bar
└── types/                 # TypeScript types
    └── index.ts           # Type definitions
```

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **HTTP Client**: Fetch API
- **Real-time**: Server-Sent Events (SSE)

## Development

- **Build**: `npm run build`
- **Lint**: `npm run lint`
- **Start**: `npm start` (production)

## Integration

The frontend communicates with the FastAPI backend via:

- REST API calls for data fetching
- Server-Sent Events for real-time updates
- JSON data exchange matching backend schemas
