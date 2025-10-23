import React, { useState } from 'react'
import { ReactFlow, Background, Controls, MiniMap } from 'reactflow'
import 'reactflow/dist/style.css'

const WorkflowBuilder: React.FC = () => {
  const [nodes, setNodes] = useState([])
  const [edges, setEdges] = useState([])

  return (
    <div className="flex h-full">
      {/* Left Panel - Node Palette */}
      <div className="w-80 bg-white border-r border-gray-200 p-4 overflow-y-auto">
        <h2 className="text-lg font-semibold mb-4 text-gray-800">Node Palette</h2>

        {/* Triggers */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-600 mb-2">Triggers</h3>
          <div className="space-y-2">
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-md cursor-pointer hover:bg-blue-100 transition-colors">
              <div className="text-sm font-medium text-blue-800">Webhook</div>
              <div className="text-xs text-blue-600">HTTP endpoint trigger</div>
            </div>
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-md cursor-pointer hover:bg-blue-100 transition-colors">
              <div className="text-sm font-medium text-blue-800">Schedule</div>
              <div className="text-xs text-blue-600">Time-based trigger</div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-600 mb-2">Actions</h3>
          <div className="space-y-2">
            <div className="p-3 bg-green-50 border border-green-200 rounded-md cursor-pointer hover:bg-green-100 transition-colors">
              <div className="text-sm font-medium text-green-800">HTTP Request</div>
              <div className="text-xs text-green-600">Make API calls</div>
            </div>
            <div className="p-3 bg-green-50 border border-green-200 rounded-md cursor-pointer hover:bg-green-100 transition-colors">
              <div className="text-sm font-medium text-green-800">Email</div>
              <div className="text-xs text-green-600">Send emails</div>
            </div>
          </div>
        </div>

        {/* Logic */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-600 mb-2">Logic</h3>
          <div className="space-y-2">
            <div className="p-3 bg-purple-50 border border-purple-200 rounded-md cursor-pointer hover:bg-purple-100 transition-colors">
              <div className="text-sm font-medium text-purple-800">If/Else</div>
              <div className="text-xs text-purple-600">Conditional logic</div>
            </div>
            <div className="p-3 bg-purple-50 border border-purple-200 rounded-md cursor-pointer hover:bg-purple-100 transition-colors">
              <div className="text-sm font-medium text-purple-800">Filter</div>
              <div className="text-xs text-purple-600">Data filtering</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Canvas */}
      <div className="flex-1 relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={() => {}}
          onEdgesChange={() => {}}
          className="bg-gray-50"
          fitView
        >
          <Background />
          <Controls />
          <MiniMap />
        </ReactFlow>

        {/* Toolbar */}
        <div className="absolute top-4 left-4 z-10 flex space-x-2">
          <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
            Run
          </button>
          <button className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors">
            Save
          </button>
          <button className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors">
            Export
          </button>
        </div>
      </div>

      {/* Right Panel - Properties */}
      <div className="w-80 bg-white border-l border-gray-200 p-4 overflow-y-auto">
        <h2 className="text-lg font-semibold mb-4 text-gray-800">Properties</h2>
        <div className="text-sm text-gray-500">
          Select a node to configure its properties
        </div>
      </div>
    </div>
  )
}

export default WorkflowBuilder
