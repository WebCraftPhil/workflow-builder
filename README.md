# n8n Visual Workflow Builder

A modern, visual workflow builder interface for **n8n**, designed as a no-code automation platform inspired by Node-RED and Zapier. This application provides an intuitive drag-and-drop canvas environment for creating, editing, and managing n8n workflows.

## 🚀 Features

- **Visual Canvas**: Drag-and-drop workflow creation with ReactFlow
- **Comprehensive Node Library**: Triggers, Actions, Logic, Data Transformation, and AI nodes
- **Real-time Validation**: Instant feedback on workflow configuration
- **n8n Integration**: Full JSON compatibility and API synchronization
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **TypeScript**: Fully typed for better development experience
- **Modern UI**: Built with React, TypeScript, and Tailwind CSS

## 📋 Project Structure

```
workflow-builder/
├── src/
│   ├── components/          # React components
│   │   ├── WorkflowBuilder.tsx    # Main workflow canvas
│   │   └── ...
│   ├── hooks/               # Custom React hooks
│   ├── stores/              # State management (Zustand)
│   ├── types/               # TypeScript type definitions
│   ├── utils/               # Utility functions
│   ├── services/            # API and external service integrations
│   ├── App.tsx              # Main app component
│   ├── main.tsx             # React entry point
│   └── index.css            # Global styles
├── public/                  # Static assets
├── package.json             # Dependencies and scripts
├── tsconfig.json            # TypeScript configuration
├── vite.config.ts           # Vite build configuration
└── tailwind.config.js       # Tailwind CSS configuration
```

## 🛠️ Tech Stack

- **Frontend**: React 18 + TypeScript
- **Canvas**: ReactFlow for drag-and-drop workflow creation
- **Styling**: Tailwind CSS
- **Build Tool**: Vite
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Real-time**: Socket.io for live collaboration

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm
- Modern web browser

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd workflow-builder
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Open your browser**
   Navigate to `http://localhost:3000`

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## 📖 Usage

### Creating Workflows

1. **Select Nodes**: Drag nodes from the left palette onto the canvas
2. **Connect Nodes**: Click and drag between node connection points
3. **Configure Properties**: Select nodes to configure their parameters in the right panel
4. **Validate**: Real-time validation provides immediate feedback
5. **Test**: Use the toolbar to run and test your workflow

### Node Types

- **Triggers**: Webhook, Schedule, Manual, Email, Database, File, API
- **Actions**: HTTP Request, Email, Database, File, Message Queue, Notifications
- **Logic**: If/Else, Switch, Loop, Wait/Delay, Error Handler, Filter, Sort
- **Data Transformation**: JSON, XML, CSV, Text, Date/Time, Math, Regex, Template
- **AI & ML**: OpenAI, Anthropic, Hugging Face, Vector DB, Text Analysis, Image Analysis

## 🔗 n8n Integration

The workflow builder is fully compatible with n8n's workflow format:

### Export/Import
- Export workflows as n8n-compatible JSON
- Import existing n8n workflows
- Template sharing and management

### Real-time Sync
- WebSocket connection for live collaboration
- REST API integration for workflow management
- OAuth and credential management

## 🎨 Design Specification

For detailed UI/UX specifications, see [`workflow-builder-spec.md`](workflow-builder-spec.md) which includes:

- Complete UI layout and interaction design
- Technical architecture diagrams
- Implementation roadmap
- Advanced feature specifications

## 🔧 Development

### Project Structure Details

```
src/
├── components/          # Reusable UI components
│   ├── WorkflowBuilder.tsx    # Main canvas component
│   ├── NodePalette.tsx        # Node selection sidebar
│   ├── PropertiesPanel.tsx    # Node configuration panel
│   └── ...
├── stores/              # Zustand state stores
│   ├── workflowStore.ts       # Workflow state management
│   ├── nodeStore.ts           # Node state management
│   └── ...
├── types/               # TypeScript definitions
│   ├── workflow.ts            # Workflow type definitions
│   ├── node.ts                # Node type definitions
│   └── ...
├── services/            # External API integrations
│   ├── n8nApi.ts              # n8n server communication
│   ├── validation.ts          # Workflow validation
│   └── ...
```

### Adding New Node Types

1. Define the node type in `src/types/node.ts`
2. Create the node component in `src/components/nodes/`
3. Add to the palette in `NodePalette.tsx`
4. Implement configuration in `PropertiesPanel.tsx`

## 📚 Learn More

- [ReactFlow Documentation](https://reactflow.dev/)
- [n8n API Documentation](https://docs.n8n.io/api/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Guide](https://tailwindcss.com/docs)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by [Node-RED](https://nodered.org/) and [Zapier](https://zapier.com/)
- Built with [ReactFlow](https://reactflow.dev/) and [n8n](https://n8n.io/)
- Styled with [Tailwind CSS](https://tailwindcss.com/)