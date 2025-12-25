import { useCallback, useEffect, useMemo, useRef, DragEvent, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  BackgroundVariant,
  Node,
  Edge,
  ReactFlowInstance,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { useCanvasStore, ProcessConfig } from "./store/canvasStore";
import { nodeTypes } from "./components/nodes";
import { vscodeApi } from "./vscode";
import { Palette } from "./components/Palette";
import { PropertiesPanel } from "./components/PropertiesPanel";
import { graphToDsl, generateNodeId } from "./utils/graphToDsl";
import { applyTrainLaneLayout } from "./utils/trainLaneLayout";
import { useUndoRedo } from "./hooks/useUndoRedo";
import { useKeyboardShortcuts, getShortcutDisplay } from "./hooks/useKeyboardShortcuts";
import { exportAsPng, exportAsSvg } from "./utils/exportCanvas";

function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [reactFlowInstance, setReactFlowInstance] = useState<ReactFlowInstance | null>(null);

  // Track if we're applying undo/redo to avoid taking snapshot
  const isUndoRedoRef = useRef(false);

  const {
    setProcessName,
    setFilePath,
    processConfig,
    setProcessConfig,
    selectedNodeId,
    setSelectedNode,
    clearSelection,
    isDirty,
    setDirty,
    isPaletteCollapsed,
    togglePalette,
    resetCanvas,
  } = useCanvasStore();

  // Undo/Redo hook
  const {
    canUndo,
    canRedo,
    takeSnapshot,
    undo,
    redo,
    clear: clearHistory,
  } = useUndoRedo({ maxHistory: 50 });

  // Get selected node data
  const selectedNode = useMemo((): Node | null => {
    if (!selectedNodeId) return null;
    return nodes.find((n: Node) => n.id === selectedNodeId) || null;
  }, [selectedNodeId, nodes]);

  /**
   * Take a snapshot for undo/redo history.
   * Should be called after any user action that modifies nodes/edges.
   */
  const recordSnapshot = useCallback(() => {
    if (!isUndoRedoRef.current) {
      takeSnapshot(nodes, edges);
    }
  }, [nodes, edges, takeSnapshot]);

  // Handle undo action
  const handleUndo = useCallback(() => {
    const previousState = undo();
    if (previousState) {
      isUndoRedoRef.current = true;
      setNodes(previousState.nodes);
      setEdges(previousState.edges);
      setDirty(true);
      isUndoRedoRef.current = false;
    }
  }, [undo, setNodes, setEdges, setDirty]);

  // Handle redo action
  const handleRedo = useCallback(() => {
    const nextState = redo();
    if (nextState) {
      isUndoRedoRef.current = true;
      setNodes(nextState.nodes);
      setEdges(nextState.edges);
      setDirty(true);
      isUndoRedoRef.current = false;
    }
  }, [redo, setNodes, setEdges, setDirty]);

  // Handle new connections
  const onConnect = useCallback(
    (connection: Connection) => {
      recordSnapshot();
      setEdges((eds) => addEdge(connection, eds));
      setDirty(true);
    },
    [setEdges, setDirty, recordSnapshot]
  );

  // Handle drag over for palette drops
  const onDragOver = useCallback((event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  // Handle drop from palette
  const onDrop = useCallback(
    (event: DragEvent<HTMLDivElement>) => {
      event.preventDefault();

      const type = event.dataTransfer.getData("application/reactflow-type");
      const dataString = event.dataTransfer.getData("application/reactflow-data");

      if (!type || !reactFlowInstance) {
        return;
      }

      // Get drop position
      const position = reactFlowInstance.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      // Parse default data
      let defaultData: Record<string, unknown> = {};
      try {
        defaultData = JSON.parse(dataString);
      } catch (e) {
        console.warn("Failed to parse node data");
      }

      // Generate unique ID
      const id = generateNodeId(type, nodes);

      // Create new node
      const newNode: Node = {
        id,
        type,
        position,
        data: { ...defaultData, label: (defaultData.label as string) || type },
      };

      recordSnapshot();
      setNodes((nds) => nds.concat(newNode));
      setDirty(true);
      setSelectedNode(id);
    },
    [reactFlowInstance, nodes, setNodes, setDirty, setSelectedNode, recordSnapshot]
  );

  // Handle node data changes from properties panel
  const handleNodeChange = useCallback(
    (nodeId: string, data: Record<string, unknown>) => {
      recordSnapshot();
      setNodes((nds) =>
        nds.map((node) =>
          node.id === nodeId ? { ...node, data } : node
        )
      );
      setDirty(true);
    },
    [setNodes, setDirty, recordSnapshot]
  );

  // Handle process config changes
  const handleProcessChange = useCallback(
    (config: Partial<ProcessConfig>) => {
      setProcessConfig(config);
      if (config.processName) {
        setProcessName(config.processName);
      }
    },
    [setProcessConfig, setProcessName]
  );

  // Handle node deletion
  const handleDeleteNode = useCallback(
    (nodeId: string) => {
      recordSnapshot();
      setNodes((nds) => nds.filter((node) => node.id !== nodeId));
      setEdges((eds) => eds.filter((edge) => edge.source !== nodeId && edge.target !== nodeId));
      clearSelection();
      setDirty(true);
    },
    [setNodes, setEdges, clearSelection, setDirty, recordSnapshot]
  );

  // Delete selected node (for keyboard shortcut)
  const handleDeleteSelected = useCallback(() => {
    if (selectedNodeId) {
      handleDeleteNode(selectedNodeId);
    }
  }, [selectedNodeId, handleDeleteNode]);

  // Select all nodes
  const handleSelectAll = useCallback(() => {
    // React Flow handles multi-select internally, but we can select first node
    if (nodes.length > 0) {
      setSelectedNode(nodes[0].id);
    }
  }, [nodes, setSelectedNode]);

  // Generate DSL and send to extension
  const handleGenerateDsl = useCallback(() => {
    const dsl = graphToDsl(nodes, edges, processConfig);
    vscodeApi.postMessage({ type: "generatedDsl", data: dsl });
  }, [nodes, edges, processConfig]);

  // Save current canvas state
  const handleSave = useCallback(() => {
    const canvasState = {
      nodes,
      edges,
      processConfig,
    };
    vscodeApi.postMessage({ type: "save", data: canvasState });
    setDirty(false);
  }, [nodes, edges, processConfig, setDirty]);

  // Create new process
  const handleNew = useCallback(() => {
    if (isDirty) {
      // In a real app, we'd show a confirmation dialog
      // For now, just reset
    }
    resetCanvas();
    setNodes([]);
    setEdges([]);
    clearHistory();
  }, [isDirty, resetCanvas, setNodes, setEdges, clearHistory]);

  // Re-apply train-lane layout
  const handleRelayout = useCallback(() => {
    recordSnapshot();
    const layoutedNodes = applyTrainLaneLayout(nodes, edges);
    setNodes(layoutedNodes);
  }, [nodes, edges, setNodes, recordSnapshot]);

  // Keyboard shortcuts
  useKeyboardShortcuts({
    onUndo: handleUndo,
    onRedo: handleRedo,
    onSave: handleSave,
    onDelete: handleDeleteSelected,
    onSelectAll: handleSelectAll,
    onEscape: clearSelection,
  });

  // Listen for messages from VS Code extension
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      const message = event.data;

      switch (message.type) {
        case "loadGraph":
          // Load graph data from CLI parse output
          const { data, filePath: fp } = message;
          setProcessName(data.processName || "Untitled");
          setFilePath(fp);

          // Update process config
          setProcessConfig({
            processName: data.processName || "new_process",
            parallelism: data.parallelism,
            timeField: data.timeField,
            watermarkDelay: data.watermarkDelay,
          });

          // Convert graph data to React Flow format
          const flowNodes: Node[] = data.nodes.map((node: any) => ({
            id: node.id,
            type: node.type,
            position: { x: 0, y: 0 }, // Will be set by layout
            data: node.data,
          }));

          const flowEdges: Edge[] = data.edges.map((edge: any) => ({
            id: edge.id,
            source: edge.source,
            target: edge.target,
            sourceHandle: edge.sourceHandle,
            targetHandle: edge.targetHandle,
            label: edge.label,
            type: "smoothstep",
            animated: edge.type === "async",
          }));

          // Apply train-lane layout
          const layoutedNodes = applyTrainLaneLayout(flowNodes, flowEdges);

          setNodes(layoutedNodes);
          setEdges(flowEdges);
          clearSelection();
          setDirty(false);
          clearHistory();

          // Take initial snapshot after loading
          setTimeout(() => takeSnapshot(layoutedNodes, flowEdges), 0);
          break;

        case "error":
          console.error("Error from extension:", message.message);
          break;

        case "validationResult":
          if (message.success) {
            console.log("Validation passed");
          } else {
            console.error("Validation failed:", message.errors);
          }
          break;
      }
    };

    window.addEventListener("message", handleMessage);

    // Tell extension we're ready
    vscodeApi.postMessage({ type: "ready" });

    return () => window.removeEventListener("message", handleMessage);
  }, [setNodes, setEdges, setProcessName, setFilePath, setProcessConfig, clearSelection, setDirty, clearHistory, takeSnapshot]);

  // Handle node selection
  const onNodeClick = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      setSelectedNode(node.id);
    },
    [setSelectedNode]
  );

  // Handle background click (deselect)
  const onPaneClick = useCallback(() => {
    clearSelection();
  }, [clearSelection]);

  return (
    <div className="w-full h-full flex flex-col">
      {/* Header / Toolbar */}
      <div className="h-10 px-4 flex items-center justify-between border-b border-vscode-border bg-vscode-bg">
        <div className="flex items-center gap-2">
          <span className="text-vscode-accent font-semibold">
            {processConfig.processName || "New Process"}
          </span>
          {isDirty && (
            <span className="text-xs text-yellow-500">●</span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {/* Undo/Redo buttons */}
          <button
            onClick={handleUndo}
            disabled={!canUndo}
            className="px-2 py-1 text-xs bg-vscode-button text-vscode-button-fg rounded hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed"
            title={`Undo (${getShortcutDisplay("undo")})`}
          >
            ↶
          </button>
          <button
            onClick={handleRedo}
            disabled={!canRedo}
            className="px-2 py-1 text-xs bg-vscode-button text-vscode-button-fg rounded hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed"
            title={`Redo (${getShortcutDisplay("redo")})`}
          >
            ↷
          </button>
          <div className="w-px h-5 bg-vscode-border mx-1" />
          <button
            onClick={handleNew}
            className="px-3 py-1 text-xs bg-vscode-button text-vscode-button-fg rounded hover:opacity-90"
            title="New process"
          >
            New
          </button>
          <button
            onClick={handleSave}
            className="px-3 py-1 text-xs bg-vscode-button text-vscode-button-fg rounded hover:opacity-90"
            title={`Save canvas state (${getShortcutDisplay("save")})`}
          >
            Save
          </button>
          <button
            onClick={handleGenerateDsl}
            className="px-3 py-1 text-xs bg-green-600 text-white rounded hover:opacity-90"
            title="Generate ProcDSL code"
          >
            Generate DSL
          </button>
          <button
            onClick={handleRelayout}
            className="px-3 py-1 text-xs bg-vscode-button text-vscode-button-fg rounded hover:opacity-90"
            title="Re-apply train-lane layout"
          >
            Layout
          </button>
          <div className="w-px h-5 bg-vscode-border mx-1" />
          <button
            onClick={() => vscodeApi.postMessage({ type: "openInEditor" })}
            className="px-3 py-1 text-xs bg-vscode-button text-vscode-button-fg rounded hover:opacity-90"
          >
            Open DSL
          </button>
          <button
            onClick={() => vscodeApi.postMessage({ type: "validate" })}
            className="px-3 py-1 text-xs bg-vscode-button text-vscode-button-fg rounded hover:opacity-90"
          >
            Validate
          </button>
          <div className="w-px h-5 bg-vscode-border mx-1" />
          <button
            onClick={() => exportAsPng()}
            className="px-3 py-1 text-xs bg-vscode-button text-vscode-button-fg rounded hover:opacity-90"
            title="Export canvas as PNG"
          >
            PNG
          </button>
          <button
            onClick={() => exportAsSvg()}
            className="px-3 py-1 text-xs bg-vscode-button text-vscode-button-fg rounded hover:opacity-90"
            title="Export canvas as SVG"
          >
            SVG
          </button>
        </div>
      </div>

      {/* Main area: Palette + Canvas + Properties */}
      <div className="flex-1 flex">
        {/* Left: Component Palette */}
        <Palette isCollapsed={isPaletteCollapsed} onToggle={togglePalette} />

        {/* Center: Canvas */}
        <div
          className="flex-1"
          onDrop={onDrop}
          onDragOver={onDragOver}
        >
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            onPaneClick={onPaneClick}
            onInit={setReactFlowInstance}
            nodeTypes={nodeTypes}
            fitView
            snapToGrid
            snapGrid={[15, 15]}
            defaultEdgeOptions={{
              type: "smoothstep",
            }}
          >
            <Background variant={BackgroundVariant.Dots} gap={15} size={1} />
            <Controls />
            <MiniMap
              nodeColor={(node) => {
                switch (node.type) {
                  case "stream":
                    return "#3b82f6";
                  case "xform-ref":
                    return "#22c55e";
                  case "rules-ref":
                    return "#a855f7";
                  case "route":
                    return "#f59e0b";
                  case "window":
                    return "#06b6d4";
                  case "join":
                    return "#ec4899";
                  case "marker":
                    return "#ef4444";
                  default:
                    return "#6b7280";
                }
              }}
            />
          </ReactFlow>
        </div>

        {/* Right: Properties Panel */}
        <PropertiesPanel
          selectedNode={selectedNode}
          processInfo={processConfig}
          onNodeChange={handleNodeChange}
          onProcessChange={handleProcessChange}
          onDeleteNode={handleDeleteNode}
        />
      </div>
    </div>
  );
}

export default App;
