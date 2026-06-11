import { Chip, Box, Typography } from "@mui/material";

const levelColor: Record<string, "success" | "warning" | "error" | "default"> = {
  low: "success",
  medium: "warning",
  high: "error",
  critical: "error",
};

interface Props {
  impactLevel: string;
  affectedServices: string[];
}

export default function ImpactSummary({ impactLevel, affectedServices }: Props) {
  return (
    <Box>
      <Typography variant="subtitle2" gutterBottom>
        Impact Summary
      </Typography>
      <Chip
        label={impactLevel.toUpperCase()}
        color={levelColor[impactLevel] ?? "default"}
        sx={{ mb: 1, fontWeight: 700 }}
      />
      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5, mt: 1 }}>
        {affectedServices.map((s) => (
          <Chip key={s} label={s} size="small" variant="outlined" />
        ))}
      </Box>
    </Box>
  );
}
