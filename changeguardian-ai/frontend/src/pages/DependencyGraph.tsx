import { Box, Typography, List, ListItem, ListItemText, Paper } from "@mui/material";
import CytoscapeGraph from "../graphs/CytoscapeGraph";
import { AnalyzeChangeResponse } from "../services/api";

interface Props {
  result: AnalyzeChangeResponse | null;
}

function inferEdges(services: string[]): Array<{ source: string; target: string }> {
  // Deterministic demo edges based on naming conventions
  const edges: Array<{ source: string; target: string }> = [];
  services.forEach((s) => {
    if (s.includes("order") && services.includes("payment-service")) {
      edges.push({ source: s, target: "payment-service" });
    }
    if (s.includes("payment") && services.includes("postgres-payments")) {
      edges.push({ source: s, target: "postgres-payments" });
    }
    if (s.includes("notification") && services.includes("order-service")) {
      edges.push({ source: s, target: "order-service" });
    }
  });
  return edges;
}

export default function DependencyGraph({ result }: Props) {
  if (!result) {
    return (
      <Box sx={{ mt: 4, textAlign: "center" }}>
        <Typography color="text.secondary">No analysis result yet. Submit a change first.</Typography>
      </Box>
    );
  }

  const { affected_services } = result;

  return (
    <Box sx={{ maxWidth: 900, mx: "auto", mt: 4, px: 2 }}>
      <Typography variant="h5" fontWeight={700} gutterBottom>
        Dependency Graph
      </Typography>
      <CytoscapeGraph services={affected_services} edges={inferEdges(affected_services)} />
      <Paper sx={{ mt: 3, p: 2 }} variant="outlined">
        <Typography variant="subtitle1" fontWeight={600} gutterBottom>
          Service Explorer
        </Typography>
        <List dense>
          {affected_services.map((s) => (
            <ListItem key={s}>
              <ListItemText primary={s} />
            </ListItem>
          ))}
        </List>
      </Paper>
    </Box>
  );
}
