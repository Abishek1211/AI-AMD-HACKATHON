import { Box, Typography, LinearProgress } from "@mui/material";

interface Props {
  score: number;
}

function riskColor(score: number): "success" | "warning" | "error" {
  if (score < 40) return "success";
  if (score < 70) return "warning";
  return "error";
}

export default function RiskGauge({ score }: Props) {
  const color = riskColor(score);
  return (
    <Box>
      <Typography variant="subtitle2" gutterBottom>
        Risk Score
      </Typography>
      <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
        <Box sx={{ flex: 1 }}>
          <LinearProgress variant="determinate" value={score} color={color} sx={{ height: 12, borderRadius: 6 }} />
        </Box>
        <Typography variant="h6" color={`${color}.main`} sx={{ minWidth: 40 }}>
          {score}
        </Typography>
      </Box>
    </Box>
  );
}
