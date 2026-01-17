# AutoNote AI Backend

A FastAPI backend for an AI-powered note organization system with Firebase integration.

## Features

- **User Authentication**: Signup/Login with secure password hashing
- **AI-Powered Organization**: Automatically organizes notes using AI
- **Note Management**: Create, read, update, and delete notes
- **Firebase Integration**: Cloud storage with Firestore
- **Vercel Deployment**: Ready for serverless deployment

## Local Development Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Firebase**:
   - Place your Firebase credentials JSON file in the project root
   - Update the `FIREBASE_CRED_PATH` in `AutoMated.py` if needed

3. **Run the server**:
   ```bash
   python AutoMated.py
   ```
   The API will be available at `http://localhost:8000`

## Deploy to Vercel

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for detailed deployment instructions.

### Quick Deploy Steps:
1. Install Vercel CLI: `npm install -g vercel`
2. Run: `vercel`
3. Set environment variables in Vercel dashboard
4. Deploy: `vercel --prod`

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register a new user
- `POST /api/auth/login` - Login and get auth token

### Notes
- `POST /api/notes/organize` - Get AI suggestions for note organization
- `POST /api/notes` - Create or merge a note
- `GET /api/notes` - Get all user notes
- `GET /api/notes/{id}` - Get a specific note
- `PUT /api/notes/{id}` - Update a note
- `DELETE /api/notes/{id}` - Delete a note

## Project Structure

```
PythonProject2/
├── api/
│   └── index.py          # Vercel serverless function entry point
├── AutoMated.py          # Local development server
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies
├── DEPLOYMENT.md         # Deployment guide
└── README.md            # This file
```

## Security Notes

⚠️ **Important**: 
- Keep your Firebase credentials file secure and never commit it to version control
- Use environment variables for production deployment
- The `.gitignore` file excludes all sensitive files
