import { Box, Typography, CircularProgress } from "@mui/material";

interface Props {
  confidence: number;
}

export default function ConfidenceMeter({ confidence }: Props) {
  return (
    <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 1 }}>
      <Typography variant="subtitle2">Confidence</Typography>
      <Box sx={{ position: "relative", display: "inline-flex" }}>
        <CircularProgress variant="determinate" value={confidence} size={80} thickness={5} color="info" />
        <Box
          sx={{
            top: 0,
            left: 0,
            bottom: 0,
            right: 0,
            position: "absolute",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <Typography variant="caption" color="text.secondary" fontWeight={700}>
            {confidence}%
          </Typography>
        </Box>
      </Box>
    </Box>
  );
}
