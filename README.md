# RL Elevator Simulation System

An AI-powered intelligent elevator scheduling system using Reinforcement Learning (PPO algorithm) to optimize elevator operations and reduce passenger wait times in multi-floor buildings.

## 📋 Project Overview

This is a university AI engineering project that combines machine learning with real-world building automation. The system uses **Proximal Policy Optimization (PPO)** from Stable Baselines3 to train an intelligent agent that learns optimal elevator dispatching strategies. The frontend provides real-time visualization and monitoring of elevator operations through a modern web dashboard.

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────┐
│   Frontend (Next.js)                    │
│   - Real-time Dashboard                 │
│   - WebSocket Communication             │
│   - Elevator Visualization              │
└──────────────┬──────────────────────────┘
               │ WebSocket (ws://localhost:8000/ws/step)
               ↓
┌─────────────────────────────────────────┐
│   Backend (FastAPI)                     │
│   - Smart Elevator Environment          │
│   - PPO AI Agent                        │
│   - Real-time Step Processing           │
└─────────────────────────────────────────┘
```

## 🛠️ Technology Stack

### Frontend

- **Framework**: Next.js 16.2.4
- **Language**: TypeScript
- **UI Library**: React 19.2.4
- **Styling**: Tailwind CSS 4
- **Real-time**: react-use-websocket
- **Build Tool**: Next.js built-in

### Backend

- **Framework**: FastAPI 0.135.1
- **Language**: Python
- **ML Library**: Stable Baselines3 (PPO)
- **Environment**: Custom Gym environment
- **Real-time**: WebSocket support
- **Scientific**: NumPy, OpenCV, MediaPipe, Gymnasium

## 📋 Prerequisites

### System Requirements

- **Node.js**: 18+ (for frontend)
- **Python**: 3.9+ (for backend)
- **npm** or **yarn** (for Node.js package management)

## ⚙️ Installation & Setup

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirementst.txt

# Verify installation
python -c "import stable_baselines3; print('Stable Baselines3 installed successfully')"
```

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install
# or
yarn install

# Create environment configuration file
cp .env.example .env.local
# OR manually create .env.local with the configuration shown in the Configuration section
```

## 🚀 Running the Application

### Terminal 1: Start the Backend Server

```bash
cd backend
python server.py
```

The backend will start on `http://localhost:8000` with:

- REST API endpoints
- WebSocket server at `ws://localhost:8000/ws/step`
- CORS enabled for frontend communication

### Terminal 2: Start the Frontend Development Server

```bash
cd frontend
npm run dev
# or
yarn dev
```

The frontend will be available at `http://localhost:3000`

### Access the Dashboard

Open your browser and navigate to:

```
http://localhost:3000
```

You should see the **RL Elevator Simulation Dashboard** with:

- ✅ Real-time connection status
- 📊 Simulation metrics (steps, total score, rewards)
- 🏢 Hall calls display (up/down requests per floor)
- 🛗 Elevator car status and car calls
- 📈 Performance monitoring

## 📁 Project Structure

```
FinalProject/
├── backend/
│   ├── server.py                 # FastAPI server entry point
│   ├── requirementst.txt         # Python dependencies
│   └── model/
│       ├── enviroment_final.py   # Gym environment definition
│       ├── ppo_smart_elevator_final    # Trained PPO model
│       └── vec_normalize_final.pkl     # Vector normalization
│
└── frontend/
    ├── src/
    │   ├── app/
    │   │   ├── page.tsx          # Main dashboard component
    │   │   ├── layout.tsx        # Layout wrapper
    │   │   └── globals.css       # Global styles
    │   ├── components/
    │   │   ├── ElevatorSystem.tsx        # System visualization
    │   │   └── ElevatorShaft.tsx        # Individual elevator shaft
    │   └── hook/
    │       └── useElevatorWebsocket.ts  # WebSocket hook
    ├── package.json              # Node.js dependencies
    ├── tsconfig.json             # TypeScript configuration
    ├── next.config.ts            # Next.js configuration
    └── README.md                 # This file
```

## 🎯 Key Features

### AI Agent

- ✨ Trained PPO model for optimal elevator dispatch decisions
- 🧠 Learns from reward signals (waiting time, travel efficiency)
- 📊 Continuous learning and improvement

### Real-time Dashboard

- 🔄 Live WebSocket connection status
- 📈 Step-by-step simulation progress
- 💰 Total score and per-step reward metrics
- 🏗️ Hall call buttons (up/down requests)
- 🛗 Elevator car states and destinations
- 📊 Visual representation of building state

### Backend Services

- ⚡ FastAPI for high-performance async handling
- 🔌 WebSocket for real-time communication
- 🔐 CORS middleware for secure frontend integration
- 🎮 Gym-based environment for RL training

## 🔧 Configuration

### Environment Variables (.env.local)

Create a `.env.local` file in the `frontend/` directory to configure the frontend application:

```env
# WebSocket connection to backend
NEXT_PUBLIC_WS_URL=ws://127.0.0.1:8000/ws/step
```

**Note:** Variables prefixed with `NEXT_PUBLIC_` are exposed to the browser and can be accessed in client-side code.

### Backend Configuration (server.py)

- **Port**: 8000
- **CORS**: Allows requests from all origins (`allow_origins=["*"]`)
- **WebSocket Endpoint**: `/ws/step`

### Frontend Configuration

- **Default Backend URL**: `ws://127.0.0.1:8000/ws/step` (override in `.env.local`)
- **Port**: 3000
- **Building Configuration**:
  - Number of elevators: 6
  - Number of floors: 10

## 🐛 Troubleshooting

### WebSocket Connection Issues

- Ensure backend is running on `localhost:8000`
- Check firewall settings
- Verify CORS is enabled in FastAPI

### Module Import Errors (Backend)

- Reinstall dependencies: `pip install --force-reinstall -r requirementst.txt`
- Check Python version compatibility

### Frontend Blank Page

- Clear browser cache and hard refresh (Ctrl+Shift+R)
- Check browser console for WebSocket errors (F12)
- Verify backend is running

## 📚 Learning Resources

- [Stable Baselines3 Documentation](https://stable-baselines3.readthedocs.io/)
- [Gym Environment Documentation](https://gymnasium.farama.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)

## 📄 License

This is an academic project for the course:  
**618487 ARTIFICIAL INTELLIGENCE FOR ENGINEERS**

## 👥 Development Notes

- Backend uses PPO algorithm from Stable Baselines3
- Custom Gym environment (`SmartElevatorEnv`) simulates building with multiple elevators
- Vector normalization is applied for stable training
- Frontend connects via WebSocket for real-time state updates
