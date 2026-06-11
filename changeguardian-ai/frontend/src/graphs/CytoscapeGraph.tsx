import { useEffect, useRef } from "react";
import cytoscape, { ElementDefinition } from "cytoscape";
import { Box } from "@mui/material";

interface Props {
  services: string[];
  edges?: Array<{ source: string; target: string }>;
}

function buildElements(services: string[], edges: Array<{ source: string; target: string }>): ElementDefinition[] {
  const nodes: ElementDefinition[] = services.map((s) => ({
    data: { id: s, label: s },
  }));
  const edgeEls: ElementDefinition[] = edges.map((e, i) => ({
    data: { id: `e${i}`, source: e.source, target: e.target },
  }));
  return [...nodes, ...edgeEls];
}

export default function CytoscapeGraph({ services, edges = [] }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    cyRef.current = cytoscape({
      container: containerRef.current,
      elements: buildElements(services, edges),
      style: [
        {
          selector: "node",
          style: {
            label: "data(label)",
            "background-color": "#1976d2",
            color: "#fff",
            "text-valign": "center",
            "text-halign": "center",
            "font-size": 11,
            width: 80,
            height: 30,
            shape: "round-rectangle",
          },
        },
        {
          selector: "edge",
          style: {
            width: 2,
            "line-color": "#90caf9",
            "target-arrow-color": "#90caf9",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
          },
        },
      ],
      layout: { name: "breadthfirst", directed: true, padding: 20 },
    });
    return () => cyRef.current?.destroy();
  }, [services, edges]);

  return <Box ref={containerRef} sx={{ width: "100%", height: 400, border: "1px solid #e0e0e0", borderRadius: 1 }} />;
}
