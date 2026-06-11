import { Box, Grid, Paper, Typography } from "@mui/material";
import RiskGauge from "../components/RiskGauge";
import ConfidenceMeter from "../components/ConfidenceMeter";
import ImpactSummary from "../components/ImpactSummary";
import { AnalyzeChangeResponse } from "../services/api";

interface Props {
  result: AnalyzeChangeResponse | null;
}

export default function RiskAnalysis({ result }: Props) {
  if (!result) {
    return (
      <Box sx={{ mt: 4, textAlign: "center" }}>
        <Typography color="text.secondary">No analysis result yet. Submit a change first.</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 900, mx: "auto", mt: 4, px: 2 }}>
      <Typography variant="h5" fontWeight={700} gutterBottom>
        Risk Analysis
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }} variant="outlined">
            <RiskGauge score={result.risk_score} />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, display: "flex", justifyContent: "center" }} variant="outlined">
            <ConfidenceMeter confidence={result.confidence} />
          </Paper>
        </Grid>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }} variant="outlined">
            <ImpactSummary impactLevel={result.impact_level} affectedServices={result.affected_services} />
          </Paper>
        </Grid>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }} variant="outlined">
            <Typography variant="subtitle2" gutterBottom>
              Explanation
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {result.explanation}
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
