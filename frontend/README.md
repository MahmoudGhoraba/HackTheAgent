# HackTheAgent Frontend

Next.js 13 (Pages Router) frontend for the HackTheAgent Email Brain system.

## Tech Stack

- **Next.js 13.5** - React framework with Pages Router
- **TypeScript** - Type safety
- **Tailwind CSS 3.3** - Utility-first styling
- **Axios** - HTTP client for API calls

## Getting Started

### 1. Install Dependencies

```bash
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 3. Make sure Backend is Running

The frontend connects to the backend API at `http://localhost:8000`. 

Start the backend first:
```bash
cd ../backend
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uvicorn app.main:app --reload
```

## Project Structure

```
frontend/
├── src/
│   ├── pages/              # Next.js pages (routes)
│   │   ├── _app.tsx       # App wrapper
│   │   ├── _document.tsx  # HTML document
│   │   └── index.tsx      # Home page (semantic search)
│   ├── components/         # Reusable React components
│   ├── lib/               # Utility functions and API client
│   └── styles/
│       └── globals.css    # Global styles with Tailwind
├── public/                # Static assets
├── next.config.js         # Next.js configuration
├── tailwind.config.ts     # Tailwind CSS configuration
└── tsconfig.json          # TypeScript configuration
```

## Features

### Current Features
- ✅ Semantic search interface
- ✅ Real-time search results
- ✅ Responsive design with Tailwind CSS
- ✅ Example search queries
- ✅ Score-based result ranking

### Planned Features
- [ ] RAG question answering interface
- [ ] Email loading and indexing UI
- [ ] System statistics dashboard
- [ ] Dark mode support
- [ ] Advanced filters
- [ ] Export results

## API Integration

The frontend communicates with the FastAPI backend:

- **Semantic Search**: `POST /tool/semantic/search`
- **RAG Answer**: `POST /tool/rag/answer`
- **Load Emails**: `GET /tool/emails/load`
- **Index Messages**: `POST /tool/semantic/index`

## Development

### Build for Production

```bash
npm run build
npm start
```

### Linting

```bash
npm run lint
```

## Environment Variables

Create `.env.local` for custom configuration:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Styling

This project uses Tailwind CSS with a custom color palette:

- **Primary**: Blue shades (50-900)
- **Responsive**: Mobile-first approach
- **Dark Mode**: Automatic based on system preference

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

MIT License - see LICENSE file for details