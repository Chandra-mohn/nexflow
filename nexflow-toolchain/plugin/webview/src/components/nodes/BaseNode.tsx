import { Handle, Position } from "@xyflow/react";
import { ReactNode } from "react";
import clsx from "clsx";

interface BaseNodeProps {
  label: string;
  type: string;
  typeLabel: string;
  icon: ReactNode;
  className: string;
  children?: ReactNode;
  handles?: {
    top?: boolean;
    bottom?: boolean;
    left?: boolean;
    right?: boolean;
  };
}

export function BaseNode({
  label,
  typeLabel,
  icon,
  className,
  children,
  handles = { left: true, right: true },
}: BaseNodeProps) {
  return (
    <div className={clsx("nexflow-node", className)}>
      {handles.top && (
        <Handle type="target" position={Position.Top} id="top" />
      )}
      {handles.left && (
        <Handle type="target" position={Position.Left} id="left" />
      )}

      <div className="flex items-center gap-2">
        <span className="text-lg">{icon}</span>
        <div>
          <div className="nexflow-node-label">{label}</div>
          <div className="nexflow-node-type">{typeLabel}</div>
        </div>
      </div>

      {children}

      {handles.right && (
        <Handle type="source" position={Position.Right} id="right" />
      )}
      {handles.bottom && (
        <Handle type="source" position={Position.Bottom} id="bottom" />
      )}
    </div>
  );
}
